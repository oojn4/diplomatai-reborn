import json
from langchain_community.chat_message_histories import (
    PostgresChatMessageHistory,
)

from langchain_core.messages import HumanMessage, SystemMessage
from app.settings import settings
from app.dependencies.Postgre import PostgreClient
from app.dependencies import OpenAI
from app.config import (
    PERSONA_PROMPT
)
class FunctionsTools:
    def __init__(self,):
        self.chat_completion = OpenAI.OpenAILangchain()

    def screening(self,keterangan):
        if keterangan in ["ya", "sudah", "dah", "udh", "telah", "benar"]:
            narrative = []
            narrative.append(f"Selamat, UMKM anda telah memenuhi syarat untuk ekspor !\n"
                            "**Informasi Tren Ekspor:**\n"
    "1. Sebutkan nilai ekspor produk ke india setiap tahun.\n"
    "2. Bagaimana tren volume ekspor produk ke india selama lima tahun terakhir?\n"
    "---------------------------------------------------------------------------\n"

    "**Profil Negara Tujuan:**\n"
    "1. Sebutkan profil atau karakteristik negara india.\n"
    "2. Apa yang perlu diketahui tentang negara india?\n"
    "---------------------------------------------------------------------------\n"

    "**Ketergantungan Perdagangan Internasional:**\n"
    "1. Bagaimana peran perdagangan internasional terhadap india?\n"
    "2. Seberapa besar ketergantungan india pada perdagangan internasional?\n"
    "---------------------------------------------------------------------------\n"

    "**Konsentrasi Ekspor:**\n"
    "1. Bagaimana konsentrasi ekspor atau arah perdagangan india?\n"
    "2. Apakah india memiliki pasar ekspor yang terdiversifikasi atau terkonsentrasi?\n"
    "---------------------------------------------------------------------------\n"

    "**Struktur Perdagangan Internasional:**\n"
    "1. Bagaimana struktur perdagangan india?\n"
    "2. Apakah pola perdagangan india cocok dengan pola impor negara lain?\n"
    "---------------------------------------------------------------------------\n"

    "**Informasi Atase Perdagangan dan Indonesian Trade Promotion Center (ITPC):**\n"
    "1. Sebutkan atase atau perwakilan pemerintah Indonesia di india.\n"
    "2. Dimana lokasi Indonesian Trade Promotion Center (ITPC) di india?\n"
    "---------------------------------------------------------------------------\n"

    "**Potensi Pasar dan Daya Saing Produk:**\n"
    "1. Bagaimana potensi pasar atau daya saing produk kopi di india?\n"
    "2. Apa keunggulan produk kopi dibandingkan produk lain di india?\n"
    "---------------------------------------------------------------------------\n"

    "**Strategi dan Rekomendasi Ekspor:**\n"
    "1. Bagaimana strategi ekspor produk kopi ke india?\n"
    "2. Apa rekomendasi untuk memperluas ekspor produk kopi ke india?\n"
    "---------------------------------------------------------------------------\n"

    "**Regulasi dan Syarat Mutu Produk:**\n"
    "1. Bagaimana regulasi atau aturan atau syarat mutu ekspor produk kopi ke india?\n"
    "2. Apa saja syarat mutu yang diperlukan untuk mengekspor produk kopi ke india?\n"
    "---------------------------------------------------------------------------\n"

    "**Informasi Logistik:**\n"
    "1. Bagaimana informasi logistik ekspor produk kopi dari semarang ke india?\n"
    "2. Berapa biaya logistik dari bandara ahmad yani untuk ekspor ke india?\n"
    "---------------------------------------------------------------------------\n"

    "**Deskripsi Produk:**\n"
    "1. Apa itu kopi?\n"
    "2. Bagaimana deskripsi produk kopi?\n"
    "---------------------------------------------------------------------------\n"

    "**Negara Tujuan Utama Ekspor:**\n"
    "1. Sebutkan negara tujuan ekspor dengan nilai ekspor produk kopi tertinggi.\n"
    "2. Negara tujuan ekspor mana yang paling banyak membeli produk kopi dari Indonesia?\n"
    "---------------------------------------------------------------------------\n"

    "**Produk Ekspor Utama:**\n"
    "1. Sebutkan produk dengan nilai ekspor tertinggi ke india.\n"
    "2. Produk apa yang menjadi komoditas utama ekspor ke india?\n"
    
    
    "**Generate Market Intelligence:**\n"
    "1. Buatkan laporan market intelligence produk kopi dengan domisili umkm di semarang.\n"
    "---------------------------------------------------------------------------\n"

                    )
            narrative = "\n".join(narrative)
        else:
            narrative = "Maaf, UMKM anda harus memiliki NPWP, berbentuk badan hukum, dan memiliki badan usaha"
        return narrative

    def start(self):
        '''This function is triggered from greetings'''
        greeting_message = "Hai! Saya adalah Bot Cerdas yang membantu anda dalam ekspor.\nApakah UMKM anda telah memenuhi syarat melakukan ekspor (memiliki NPWP, berbadan hukum, dan memiliki izin usaha) (udah/belum)?"
        return greeting_message
    # def screening(self,keterangan):
    #     result = PostgreClient().screening(keterangan=keterangan)
    #     return result
    def closing(self):
        '''This function is triggered from closing'''
        closing_message = "Terimakasih! sampai berjumpa kembali."
        
        return closing_message

    def tourist_count(self, location, month, year):
        """Retrieves the visitor count for a specific location, month, and year."""
        result = PostgreClient().get_tourist_cont(location=location, month=month, year=year)
        return result

    def tourist_trend(self, location, year):
        """Retrieves the monthly visitor count trend for a specific location and year ."""
        result = PostgreClient().get_monthly_trend(location=location, year=year)
        return result
    
    def top_destination_country(self, product, ascending="DESC"):
        """Retrieves the destination country with the highest export value"""
        result = PostgreClient().get_top_destination_countries(product=product, ascending=ascending)
        return result
    
    def top_product(self, destination_country, ascending="DESC"):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_top_product(destination_country=destination_country, ascending=ascending)
        return result
    
    def export_trend_prediction(self, destination_country, product):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_export_trend_prediction(destination_country=destination_country, product=product)
        return result
    
    def destination_country_profile(self, destination_country):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_destination_country_profile(destination_country=destination_country)
        return result
    
    def destination_country_trade_dependence(self, destination_country):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_destination_country_trade_dependence(destination_country=destination_country)
        return result
    
    def destination_country_export_concentration(self, destination_country):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_destination_country_export_concentration(destination_country=destination_country)
        return result
    def destination_country_trade_complementary(self, destination_country):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_destination_country_trade_complementary(destination_country=destination_country)
        return result
    def destination_country_atase_perdagangan_itpc(self, destination_country):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_destination_country_atase_itpc(destination_country=destination_country)
        return result
    def market_competitiveness(self, product,destination_country):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_market_competitiveness(product=product,destination_country=destination_country)
        return result
    def strategy_recommendation(self, product,destination_country):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_strategy_recommendation(product=product,destination_country=destination_country)
        return result
    def regulation(self, product,destination_country):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_regulation(product=product,destination_country=destination_country)
        return result
    
    def logistic_information(self, product,destination_country,domicile_regency_city):
        """Retrieves the product with the highest export value"""
        result = PostgreClient().get_logistic_information(product=product,destination_country=destination_country,domicile_regency_city = domicile_regency_city)
        return result
    import openai

    def get_closest_string(self,input_str, list_str):
        """
        Gunakan LLM untuk mendeteksi nama produk yang relevan.
        """
        # Format daftar produk menjadi string untuk prompt
        list_str = "\n ".join(list_str)

        # Buat prompt untuk LLM
        prompt = f"""
        Saya memiliki database dengan daftar nama berikut:
        {list_str}
        
        Pengguna memasukkan: "{input_str}".
        Tolong deteksi apakah nama ini mirip dengan salah satu di database. 
        Jika mirip, berikan nama yang paling relevan. Jika tidak, katakan tidak ada kecocokan.
        Cukup jawab dengan satu nama tepat seperti yang ada dalam daftar tanpa deskripsi tambahan.
        """

        # Panggil OpenAI API
        completion = self.chat_completion.get_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=prompt)])
        return completion.content

    def get_closest_export(self,product,destination_country, list_str):
        """
        Gunakan LLM untuk mendeteksi nama produk yang relevan.
        """
        # Format daftar produk menjadi string untuk prompt
        list_str = "\n ".join(list_str)

        # Buat prompt untuk LLM
        prompt = f"""
        Saya memiliki database dengan daftar nama berikut:
        {list_str}
        
        Pengguna memasukkan product: "{product}" diekspor ke negara {destination_country}.
        Tolong deteksi apakah kombinasi ekspor ini mirip dengan salah satu di database. 
        Jika mirip, berikan nama product dan destination_country yang paling relevan. Jika tidak, katakan tidak ada kecocokan."""+"""Cukup jawab dalam bentuk dictionary seperti {product:"product",destination_country:"destination_country"} seperti yang ada dalam daftar tanpa deskripsi tambahan.
        """

        # Panggil OpenAI API
        completion = self.chat_completion.get_completion(
                messages=[
                    SystemMessage(content=PERSONA_PROMPT),
                    HumanMessage(content=prompt)])
        return completion.content
    def get_product_description(self, product):
        """Retrieves the product with the highest export value"""
        product_list = PostgreClient().get_all_product()
        closest_string = self.get_closest_string(input_str=product,list_str=product_list)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            result = PostgreClient().get_product_description(product=closest_string)
            return result
        else:
            return {'narrative':f"{product} tidak ditemukan !",'attachment':None} 
    
    def get_destination_country_profile(self, destination_country):
        """Retrieves the product with the highest export value"""
        destination_country_list = PostgreClient().get_all_destination_country()
        closest_string = self.get_closest_string(input_str=destination_country,list_str=destination_country_list)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            result = PostgreClient().get_destination_country_profile(destination_country=closest_string)
            return result
        else:
            return {'narrative':f"{destination_country} tidak ditemukan !",'attachment':None} 
    def get_export_trend(self, product,destination_country):
        """Retrieves the product with the highest export value"""
        export_list = PostgreClient().get_all_export()
        closest_string = self.get_closest_export(product=product,destination_country=destination_country,list_str=export_list)
        print(closest_string)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            closest_string = json.loads(closest_string)
            print(closest_string)
            response = PostgreClient().get_export_trend(product=closest_string['product'],destination_country=closest_string['destination_country'])
            return response
        else:
            return {'narrative':f"{product} yang di ekspor ke {destination_country} tidak ditemukan !",'attachment':None} 
    def get_regulation_quality_policy(self, product,destination_country):
        """Retrieves the product with the highest export value"""
        export_list = PostgreClient().get_all_export()
        closest_string = self.get_closest_export(product=product,destination_country=destination_country,list_str=export_list)
        print(closest_string)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            closest_string = json.loads(closest_string)
            print(closest_string)
            response = PostgreClient().get_regulation_quality_policy(product=closest_string['product'],destination_country=closest_string['destination_country'])
            return response
        else:
            return {'narrative':f"{product} yang di ekspor ke {destination_country} tidak ditemukan !",'attachment':None} 
    def get_tariff_logistic(self, product,destination_country):
        """Retrieves the product with the highest export value"""
        export_list = PostgreClient().get_all_export()
        closest_string = self.get_closest_export(product=product,destination_country=destination_country,list_str=export_list)
        print(closest_string)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            closest_string = json.loads(closest_string)
            print(closest_string)
            response = PostgreClient().get_tariff_logistic(product=closest_string['product'],destination_country=closest_string['destination_country'])
            return response
        else:
            return {'narrative':f"Tarif logistik produk {product} yang di ekspor ke {destination_country} tidak ditemukan !",'attachment':None} 
    def get_trade_representative(self, destination_country):
        """Retrieves the product with the highest export value"""
        destination_country_list = PostgreClient().get_all_destination_country()
        closest_string = self.get_closest_string(input_str=destination_country,list_str=destination_country_list)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            result = PostgreClient().get_trade_representative(destination_country=closest_string)
            return result
        else:
            return {'narrative':f"{destination_country} tidak ditemukan !",'attachment':None} 
    def get_trade_dependence_index(self, destination_country):
        """Retrieves the product with the highest export value"""
        destination_country_list = PostgreClient().get_all_destination_country()
        closest_string = self.get_closest_string(input_str=destination_country,list_str=destination_country_list)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            result = PostgreClient().get_trade_dependence_index(destination_country=closest_string)
            return result
        else:
            return {'narrative':f"{destination_country} tidak ditemukan !",'attachment':None} 
    def get_export_concentration_index(self, destination_country):
        """Retrieves the product with the highest export value"""
        destination_country_list = PostgreClient().get_all_destination_country()
        closest_string = self.get_closest_string(input_str=destination_country,list_str=destination_country_list)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            result = PostgreClient().get_export_concentration_index(destination_country=closest_string)
            return result
        else:
            return {'narrative':f"{destination_country} tidak ditemukan !",'attachment':None} 
    def get_trade_complementary_index(self, destination_country):
        """Retrieves the product with the highest export value"""
        destination_country_list = PostgreClient().get_all_destination_country()
        closest_string = self.get_closest_string(input_str=destination_country,list_str=destination_country_list)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            result = PostgreClient().get_trade_complementary_index(destination_country=closest_string)
            return result
        else:
            return {'narrative':f"{destination_country} tidak ditemukan !",'attachment':None} 
    
    def market_intelligence(self, product, destination_country):
        """Retrieves the top locations with the highest visitor count for a specific year."""
        export_list = PostgreClient().get_all_export()
        closest_string = self.get_closest_export(product=product,destination_country=destination_country,list_str=export_list)
        print(closest_string)
        if closest_string and closest_string != "Tidak ada kecocokan.":
            closest_string = json.loads(closest_string)
            print(closest_string)
            product = closest_string['product']
            destination_country = closest_string['destination_country']
            result1 = PostgreClient().get_product_description(product=product)['narrative']
            result2 = PostgreClient().get_destination_country_profile(destination_country=destination_country)['narrative']
            result3 = PostgreClient().get_export_trend(product=product,destination_country=destination_country)
            result3_narrative = result3['narrative']
            result3_attachment = result3['attachment']
            result4 = PostgreClient().get_trade_dependence_index(destination_country=destination_country)['narrative']
            result5 = PostgreClient().get_export_concentration_index(destination_country=destination_country)['narrative']
            result6 = PostgreClient().get_trade_complementary_index(destination_country=destination_country)['narrative']
            
            result7 = PostgreClient().get_regulation_quality_policy(product=product,destination_country=destination_country)['narrative']
            result8 = PostgreClient().get_tariff_logistic(product=product,destination_country=destination_country)['narrative']
            result9 = PostgreClient().get_trade_representative(destination_country=destination_country)['narrative']
            result10 = PostgreClient().get_xmarket(product=product,destination_country=destination_country)
        
            return {'product_description':result1,'destination_country_profile':result2,'export_trend':result3_narrative,'export_trend_attachment':result3_attachment,'trade_dependence_index':result4,'trade_dependence_index':result4,'export_concentration_index':result5,'trade_complementary_index':result6,'regulation_quality_policy':result7,'tariff_logistic':result8,'trade_representative':result9,'market_competitiveness':result10}
        else:
            return {'narrative':f"{product} yang di ekspor ke {destination_country} tidak ditemukan !",'attachment':None} 