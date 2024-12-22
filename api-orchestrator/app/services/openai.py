import json
import traceback

from langchain_core.messages import HumanMessage, SystemMessage

from app.dependencies import PostgreClient
from app.func_call import FunctionsTools
from app.dependencies import OpenAILangchain

from app.utils import (
    build_context, history_chain_to_string, prepare_answers_to_string
)
from app.config import (
    PERSONA_PROMPT, HYDE_PROMPT, CONTEXT_AWARE_PROMPT,
    ANSWER_ASSESOR_PROMPT
)

class OpenAIServices:
    def __init__(self, history_messages : list = []):
        self.history_messages = history_chain_to_string(history_messages[-10:])
        
        # initiate instance
        self.chat_completion = OpenAILangchain()
        self.chat_completion2 = OpenAILangchain()
        self.pgch_client = PostgreClient()

    def rag_answer(self, sentence):
        '''retrieve augmented generation'''
        new_sentence = self.chat_completion.get_completion(
            messages=[HumanMessage(content=HYDE_PROMPT.format(history_chat=self.history_messages,
                                                              question=sentence))])
        # print(self.history_messages)
        # print(sentence)
        # print(new_sentence)
        embedding_query = self.chat_completion.get_embedding(new_sentence)
        # print(embedding_query)
        docs = self.pgch_client.get_context(query_embedding=embedding_query,
                                            table_name="kb_ekspor1",
                                            embedding_col="",
                                            threshold=0.5,
                                            n=5)
        print(docs)
        context_str = build_context(docs)

        messages = [SystemMessage(content=PERSONA_PROMPT)]
        print("context")
        print(context_str)

        messages.append(HumanMessage(content=CONTEXT_AWARE_PROMPT\
                                     .format(history_chat=self.history_messages, 
                                             context=context_str,
                                             question=sentence)))

        rag_answer = self.chat_completion.get_completion(messages)
        print("rag answer")
        print(rag_answer)

        return rag_answer
    
    def assess_answer(self, sentence, answers):
        """Assess which answer is the most relevant"""
        answers_str = prepare_answers_to_string(answers)
        prompt_input = [
            HumanMessage(content=ANSWER_ASSESOR_PROMPT.format(question=sentence, answers=answers_str))
        ]

        ai_result = self.chat_completion.get_completion(prompt_input)

        print(f" > Assess result : {ai_result}")

        answer = answers[int(ai_result) - 1]

        return answer

    def conversation(self, sentence: str):
        """To get response for every query that it get.

        :param session_id:
        :param sentence:
        :return:
        """
        try:
            # try chat gpt openai with tools
            # we used as single message function
            
            completion = self.chat_completion.get_chat_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=sentence)])
            answers = []
            function_answer = None
            
            if completion.additional_kwargs:
                print(" > Tools are used to answer the question")
                print(completion.additional_kwargs)
                arguments = completion.additional_kwargs["tool_calls"][0]['function']['arguments']
                print(arguments)
                # parsing the function call name
                function = completion.additional_kwargs["tool_calls"][0]['function']
                fn_name = function["name"]
                kwarg = json.loads(function["arguments"])
                
                # get the function as a function object
                function = getattr(FunctionsTools(), fn_name)
                print(fn_name)
                print(function)
                # call the function with params if there is params
                # otherwise don't call it
                function_answer = function(**kwarg) if kwarg else function()
                # self.chat_completion.disable_tools()
                print(function_answer)
                if fn_name != 'get_trade_representative':
                    print(fn_name)
                    description_function_answer = self.chat_completion2.get_completion(
                    messages=[
                        # SystemMessage(content=PERSONA_PROMPT),
                        HumanMessage(content=f"Buatkan penjelasan/deskripsi dari kalimat ini {function_answer['narrative']}")
                    ]
                    )
                else:
                    print("bener")
                    description_function_answer = None
                print(function_answer)
                if function_answer.get('attachment'):  # Cek jika 'attachment' tidak None atau kosong
                    combined_answer = f"""
                    <img src="{function_answer['attachment']}">
                    <p>{description_function_answer.content}</p>
                    """
                    answers.append(combined_answer)

                elif bool(description_function_answer):  # Cek jika 'description_function_answer' tidak kosong
                    print("tetot")
                    answers.append(description_function_answer.content)

                else:
                    answers.append(function_answer.get('narrative', ''))  # Gunakan default '' jika 'narrative' tidak ada

            print(answers)
            
            try:
                # retrieved augmented generation (RAG) flow
                print(" > Try RAG answer")
                rag_answer = self.rag_answer(sentence)
                

                print(f" > RAG answer : {rag_answer}")
                answers.append(rag_answer)

            except:
                rag_answer = completion.content
                print("exception")
            rag_answer = completion.content
            # print(rag_answer)
            if len(answers) == 2:
                print(" > Ada dua jawaban")
                # Menggunakan fungsi 'assess_answer' untuk memilih jawaban terbaik
                answer = self.assess_answer(sentence=sentence, answers=answers)
                return answer

            elif function_answer is None:  # Jika tidak ada function call
                print(" > Function call tidak terpanggil")
                return rag_answer

            elif function_answer:  # Jika function call berhasil
                if description_function_answer:  # Jika ada deskripsi tambahan
                    if function_answer.get('attachment'):  # Cek jika ada lampiran
                        combined_answer = f"""
                        <img src="{function_answer['attachment']}">
                        <p>{description_function_answer.content}</p>
                        """
                        return combined_answer
                    else:
                        # Kembalikan deskripsi saja jika tidak ada lampiran
                        return description_function_answer.content
                else:
                    # Jika tidak ada deskripsi, kembalikan narrative
                    return function_answer.get('narrative', '')

            
            # return answer

        except Exception as e:
            traceback.print_exc()

            return "Mohon maaf saat ini chatbot sedang ada gangguan, mohon tunggu beberapa saat lagi yaa..."
    def generate_market_intelligence(self, product: str, destination_country:str):
        """To get response for every query that it get.

        :param session_id:
        :param sentence:
        :return:
        """
        try:
            # try chat gpt openai with tools
            # we used as single message function
            
            completion = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"berikan market inteligence produk {product} ke negara {destination_country}")])
            answers = []
            function_answer = None
            
            if completion.additional_kwargs:
                print(" > Tools are used to answer the question")
                print(completion.additional_kwargs)
                
                # parsing the function call name
                function = completion.additional_kwargs["tool_calls"][0]['function']
                fn_name = 'market_intelligence'
                kwarg = json.loads(function["arguments"])

                # get the function as a function object
                function = getattr(FunctionsTools(), fn_name)

                # call the function with params if there is params
                # otherwise don't call it
                function_answer = function(**kwarg) if kwarg else function()

                answers.append(function_answer)
                response_destination_country_profile = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari kalimat ini {function_answer['destination_country_profile']}")
                ]
                )
                response_product_description = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari kalimat ini {function_answer['product_description']}")
                ]
                )
                response_export_trend = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari data ini {function_answer['export_trend']}")
                ]
                )
                
                response_trade_dependence_index = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari fakta ini {function_answer['trade_dependence_index']}")
                ]
                )
                
                response_export_concentration_index = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari fakta ini {function_answer['export_concentration_index']}")
                ]
                )
                response_trade_complementary_index = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari fakta ini {function_answer['trade_complementary_index']}")
                ]
                )
                response_regulation_quality_policy = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari fakta ini {function_answer['regulation_quality_policy']}")
                ]
                )
                response_tariff_logistic = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari data dan fakta ini {function_answer['tariff_logistic']}")
                ]
                )
                
                response_market_competitiveness = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan deskripsi tiga paragraf dari data dan fakta ini {function_answer['market_competitiveness']}")
                ]
                )
                all_response = response_product_description.content+"\n\n"+response_destination_country_profile.content+"\n\n"+function_answer['export_trend']+"\n\n"+response_export_trend.content+"\n\n"+response_trade_dependence_index.content+"\n\n"+response_export_concentration_index.content+"\n\n"+response_trade_complementary_index.content+"\n\n"+response_regulation_quality_policy.content+"\n\n"+response_tariff_logistic.content+"\n\n"+function_answer['trade_representative']+"\n\n"+response_market_competitiveness.content
                response_strategy = self.chat_completion.get_mi_tools_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=f"Buatkan strategi dan rekomendasi hal-hal yang dilakukan jika UMKM ingin melakukan ekspor dari penjelasan ini dalam bentuk paragraf {all_response}")
                ]
                )
                
                description_answer = {'product_description':response_product_description.content,'destination_country_profile':response_destination_country_profile.content,'data_export_trend':function_answer['export_trend'],'attachment_export_trend':function_answer['export_trend_attachment'],'export_trend':response_export_trend.content,'trade_dependence_index':response_trade_dependence_index.content, 'export_concentration_index':response_export_concentration_index.content, 'trade_complementary_index':response_trade_complementary_index.content, 'regulation_quality_policy':response_regulation_quality_policy.content,'tariff_logistic':response_tariff_logistic.content,'trade_representative':function_answer['trade_representative'],'market_competitiveness':response_market_competitiveness.content,'strategy':response_strategy.content}

            # if len(answers) == 2:
            #     print(" > Ada dua jawaban")
            #     answer = self.assess_answer(sentence="berikan market inteligence produk {product} ke negara {destination_country}", answers=answers)
            #     return answer
            # elif function_answer is not None:
            #     return function_answer
            
            return description_answer

        except Exception as e:
            traceback.print_exc()

            return "Mohon maaf saat ini aplikasi sedang ada gangguan, mohon tunggu beberapa saat lagi yaa..."
