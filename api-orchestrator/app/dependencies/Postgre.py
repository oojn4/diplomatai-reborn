import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from pgvector.psycopg2 import register_vector
from app.settings import settings
from app.dependencies import *
from app.config.constant import MONTHS, ORDERS
from langchain_core.messages import HumanMessage, SystemMessage
from rapidfuzz import process

class PostgreClient():
    def connect_db(self, connection_string):
        '''Connect to Postgres Database'''
        conn = psycopg2.connect(connection_string)

        return conn

    def get_context(self, 
                    query_embedding, 
                    n=3, 
                    table_name="", 
                    threshold=0.2,
                    embedding_col="",
                    column_name=['id', 'question','answer','embedding_question', 'embedding_answer']):
        '''Get context from certain table'''
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        embedding_array = np.array(query_embedding)

        # Register pgvector extension
        register_vector(conn)
        cur = conn.cursor()

        # column string
        column_str = ','.join(column_name)
        
        # Get the top 3 most similar documents using the KNN <=> operator
        cur.execute(
            f"SELECT {column_str} <=> %s FROM {table_name} WHERE {embedding_col} <=> %s <= {threshold} ORDER BY {embedding_col} <=> %s Limit {n}", (embedding_array, embedding_array, embedding_array,))
        
        docs = cur.fetchall()
        cur.close()

        return docs
    
    def get_top_destination_countries(self, product, limit=3, ascending="DESC"):
        """
        Retrieves the top locations with the highest visitor count for a specific year from the 'tourist_visits' table.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query = f"""
            SELECT destination_country, AVG(export_value_2023) as export_value_2023, AVG(export_volume_2023) as export_volume_2023
            FROM kb_ekspor_finalzzz
            WHERE product = '{product}'
            GROUP BY destination_country
            ORDER BY export_value_2023 {ascending}
            LIMIT {limit};
            """
        
        print(f"Paremeters: {product} {ascending}")

        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        if results:
            ascending_word = ORDERS.get(ascending)
            narrative = f"Top {len(results)} negara tujuan ekspor produk {product} dengan nilai ekspor {ascending_word} pada tahun 2023 adalah sebagai berikut:\n"
            for i, (destination_country, export_value_2023,export_volume_2023) in enumerate(results, start=1):
                narrative += f"{i}. {destination_country}: : Nilai {export_value_2023} juta USD, Volume {export_volume_2023} ribu ton\n"
        else:
            narrative = f"Tidak ada data negara tujuan ekspor untuk produk {product}."

        return narrative
    
    def get_top_product(self, destination_country, limit=3, ascending="DESC"):
        """
        Retrieves the top locations with the highest export value for specific product.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query = f"""
            SELECT product, AVG(export_value_2023) as export_value_2023, AVG(export_volume_2023) as export_volume_2023
            FROM kb_ekspor_finalzzz
            WHERE destination_country = '{destination_country}'
            GROUP BY product
            ORDER BY export_value_2023 {ascending}
            LIMIT {limit};
            """
        
        print(f"Paremeters: {destination_country} {ascending}")

        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        if results:
            ascending_word = ORDERS.get(ascending)
            narrative = f"Top {len(results)} produk di negara {destination_country} dengan nilai ekspor {ascending_word} pada tahun 2023 adalah sebagai berikut:\n"
            for i, (product, export_value_2023,export_volume_2023) in enumerate(results, start=1):
                narrative += f"{i}. {product}: Nilai {export_value_2023} juta USD, Volume {export_volume_2023} ribu ton\n"
        else:
            narrative = f"Tidak ada data produk untuk negara tujuan {destination_country}."

        return narrative
    
    def get_closest_string(self,input_str, list):
        """
        Temukan nama produk paling mirip dari daftar produk.
        """
        print(process.extractOne(input_str, list))
        closest_match, score, n = process.extractOne(input_str, list)
        if score > 50:  # Ambang batas skor kemiripan
            return closest_match
        else:
            return None
    def get_all_product(self,):
        """
        Retrieves the destination country profile.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        # Ambil daftar nama produk dari database
        cursor.execute("SELECT hs_code,name FROM products")
        product_list = ["Kode HS: "+str(row[0])+ ", Produk: "+str(row[1]) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return product_list

    def get_product_description(self, product):
        """
        Retrieves the destination country profile.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query = f"""
                    SELECT *
                    FROM products
                    WHERE name ILIKE '{product}'
                    LIMIT 1;
            """
            
            
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        if results:
            product_id,product_hs_code,product_name,product_description,product_weight = results[0]
            narrative = []
            narrative.append(f"{product_name} memiliki kode hs: {product_hs_code}. {product_name} rata-rata memiliki berat {product_weight} kg. {product_description} \n\n"
                                )
            narrative = "\n".join(narrative)
        else:
            narrative = f"{product} tidak terdaftar."
        return {
                "narrative": narrative,
                "attachment": None
            }
    def get_all_destination_country(self,):
        """
        Retrieves the destination country profile.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        # Ambil daftar nama produk dari database
        cursor.execute("SELECT name FROM destination_country")
        destination_country_list = [str(row[0]) for row in cursor.fetchall()]
        
        
        cursor.close()
        conn.close()
        return destination_country_list

    def get_destination_country_profile(self, destination_country):
        """
        Retrieves the destination country profile.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query = f"""
                SELECT id,name,geography,demography,gdp_per_capita
                FROM destination_country
                WHERE name ILIKE '{destination_country}'
                LIMIT 1;
        """
        # print(query)
        print(f"Parameters: {destination_country}")

        # Execute the query with the provided parameters
        cursor.execute(query, (
            destination_country
        ))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()

        if results:
            destination_country_id,destination_country_name,destination_country_geography,destination_country_demography,destination_country_gdp_percapita = results[0]
            narrative = []
            narrative.append(f"{destination_country_name} terletak pada {destination_country_geography}. Jumlah penduduk {destination_country_name} sebesar {destination_country_demography}. Dalam hal ekonomi, Produk Domestik Bruto (PDB) per kapita sebesar {destination_country_gdp_percapita}.\n\n"
            )
            narrative = "\n".join(narrative)
        else:
            narrative = f"{destination_country} tidak terdaftar."
        return {
                "narrative": narrative,
                "attachment": None
            }
    def get_all_export(self,):
        """
        Retrieves the destination country profile.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        # Ambil daftar nama produk dari database
        cursor.execute("""
                        SELECT products."hs_code" as products_hs_code,products."name" as products_name, destination_country."name" as destination_country_name
                        FROM export
                        LEFT JOIN products 
                        ON products.id = export.product_id 
                        LEFT JOIN destination_country
                        ON destination_country.id = export.destination_country_id
                        GROUP BY products."hs_code",products."name",destination_country."name"
                        """)
        export_list = ["Negara: "+str(row[2])+", "+"Kode HS: "+str(row[0])+ ", Produk: "+str(row[1]) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        return export_list
    def get_month_name(self,month):
        """
        Mengonversi nomor bulan (int) menjadi nama bulan (str).
        """
        month_names = {
            1: "Januari",
            2: "Februari",
            3: "Maret",
            4: "April",
            5: "Mei",
            6: "Juni",
            7: "Juli",
            8: "Agustus",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember"
        }
        return month_names.get(month, "Bulan tidak valid")

    def get_export_trend(self, destination_country, product):
        """
        Retrieves the trend export yearly based on destination country and product,
        and generates a line chart for volume and value.
        """
        # Koneksi ke database
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query = f"""
            SELECT export.*, products."name" as products_name, destination_country."name" as destination_country_name
            FROM export
            LEFT JOIN products 
            ON products.id = export.product_id 
            LEFT JOIN destination_country
            ON destination_country.id = export.destination_country_id
            WHERE destination_country."name" ILIKE  '{destination_country}' 
            AND products."name" ILIKE  '{product}'
            """
        
        print(f"Parameters: {destination_country}, {product}")

        # Eksekusi query
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Jika data ditemukan
        if results:
            # Narasi teks
            narrative = []
            narrative.append(f"Data ekspor bulanan produk {product} ke {destination_country} dari tahun 2010-2029, beserta nilai proyeksi menggunakan Facebook Prophet adalah sebagai berikut:\n")

            # Menyiapkan data untuk visualisasi
            months = []
            years = []
            volumes = []
            values = []

            for result in results:
                export_id, product_id, destination_country_id, month, year, value, volume, data_status, product_name, destination_country_name = result
                
                # Menyusun narasi
                narrative.append(f"- {self.get_month_name(month)}-{year}: {volume} ton ({value} juta USD) [{data_status}]\n")
                
                # Menambahkan data ke list
                months.append(month)
                years.append(year)
                volumes.append(volume)
                values.append(value)

            # Menggabungkan narasi menjadi teks
            narrative = "\n".join(narrative)

            # Membuat visualisasi
            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Grafik Volume
            ax1.plot(years, volumes, color='tab:blue', label='Volume (ton)')
            ax1.set_xlabel('Tahun')
            ax1.set_ylabel('Volume (ton)', color='tab:blue')
            ax1.tick_params(axis='y', labelcolor='tab:blue')

            # Grafik Value
            ax2 = ax1.twinx()
            ax2.plot(years, values, color='tab:green', label='Value (USD juta)')
            ax2.set_ylabel('Value (USD juta)', color='tab:green')
            ax2.tick_params(axis='y', labelcolor='tab:green')

            # Menambahkan judul dan legenda
            plt.title(f'Trend Ekspor {product} ke {destination_country}')
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')

            # Simpan grafik sebagai gambar base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            plt.close()

            # Menggabungkan narasi dan visualisasi
            response = {
                "narrative": narrative,
                "attachment": f"data:image/png;base64,{image_base64}"
            }
        else:
            # Jika tidak ada data
            response = {
                "narrative": "Data tidak ditemukan.",
                "attachment": None
            }

        return response

    def get_trade_dependence_index(self, destination_country):
        """
        Retrieves the trend export yearly based on destination country and product.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        
        query2 = f"""
            SELECT id,name,trade_dependence_index,export_concentration_index,trade_complementary_index FROM destination_country
            WHERE destination_country."name" ILIKE  '{destination_country}'"""
        
        print(f"Paremeters: {destination_country}")

        cursor.execute(query2)
        results2 = cursor.fetchall()
                
        cursor.close()
        conn.close()

        if results2:
            id,name,trade_dependence_index,export_concentration_index,trade_complementary_index= results2[0]
            narrative = f"Trade Dependence Index {name} sekitar {trade_dependence_index} % dari PDB."
        else:
            narrative = f"Data tidak ditemukan.."
        return {
                "narrative": narrative,
                "attachment": None
            }
    
    def get_export_concentration_index(self, destination_country):
        """
        Retrieves the trend export yearly based on destination country and product.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        
        query2 = f"""
            SELECT id,name,trade_dependence_index,export_concentration_index,trade_complementary_index FROM destination_country
            WHERE destination_country."name" ILIKE  '{destination_country}'"""
        
        print(f"Paremeters: {destination_country}")

        cursor.execute(query2)
        results2 = cursor.fetchall()
                
        cursor.close()
        conn.close()

        if results2:
            id,name,trade_dependence_index,export_concentration_index,trade_complementary_index= results2[0]
            narrative = f"Export Concentration Index {destination_country} sekitar {export_concentration_index}"
        else:
            narrative = f"Data tidak ditemukan.."
        return {
                "narrative": narrative,
                "attachment": None
            }

    def get_trade_complementary_index(self, destination_country):
        """
        Retrieves the trend export yearly based on destination country and product.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        
        query2 = f"""
            SELECT id,name,trade_dependence_index,export_concentration_index,trade_complementary_index FROM destination_country
            WHERE destination_country."name" ILIKE  '{destination_country}'"""
        
        print(f"Paremeters: {destination_country}")

        cursor.execute(query2)
        results2 = cursor.fetchall()
                
        cursor.close()
        conn.close()

        if results2:
            id,name,trade_dependence_index,export_concentration_index,trade_complementary_index= results2[0]
            narrative = f"Trade Complementary Index {destination_country} sekitar {trade_complementary_index}"
        else:
            narrative = f"Data tidak ditemukan.."
        return {
                "narrative": narrative,
                "attachment": None
            }
    
    def get_regulation_quality_policy(self, destination_country,product):
        """
        Retrieves the trend export yearly based on destination country and product.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query = f"""
            SELECT regulation.id as regulation_id,product_id,destination_country_id,regulation, quality_policy,products."name" as products_name, destination_country."name" as destination_country_name 
            FROM regulation
            LEFT JOIN products ON products.id = regulation.product_id 
            LEFT JOIN destination_country ON destination_country.id = regulation.destination_country_id
            WHERE destination_country."name" ILIKE '{destination_country}' AND products."name" ILIKE '{product}'
            """
        
        print(f"Paremeters: {destination_country} {product}")

        cursor.execute(query)
        results = cursor.fetchall()
                
        cursor.close()
        conn.close()

        if results:
            regulation_id,product_id,destination_country_id,regulation, quality_policy, product_name, destination_country_name= results[0]
            narrative = f"Regulasi ekspor negara {destination_country} untuk {product} yaitu: {regulation}. Syarat mutu ekspor negara {destination_country} untuk {product} yaitu: {quality_policy}"
        else:
            narrative = f"Tidak ada data regulasi dan syarat mutu."
        return {
                "narrative": narrative,
                "attachment": None
            }
    def get_tariff_logistic(self, destination_country,product):
        """
        Retrieves the trend export yearly based on destination country and product.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query1 = f"""
            SELECT logistic_performance_index
            FROM destination_country
            WHERE destination_country."name" ILIKE '{destination_country}'
            """
        
        print(f"Paremeters: {destination_country} {product}")

        cursor.execute(query1)
        results1 = cursor.fetchall()
        if results1:
            logistic_performance_index = str(results1[0][0])

        query2 = f"""
            SELECT max(export_tariff.year) as last_year
            FROM export_tariff
			LEFT JOIN products ON products.id = export_tariff.product_id 
            LEFT JOIN destination_country ON destination_country.id = export_tariff.destination_country_id
            WHERE destination_country."name" ILIKE '{destination_country}' AND products."name" ILIKE '{product}'
            
            """
        
        print(f"Paremeters: {destination_country} {product}")

        cursor.execute(query2)
        results2 = cursor.fetchall()
        if results2:
            last_year = str(results2[0][0])

        query3 = f"""
            SELECT export_tariff.*,products."name" as products_name, destination_country."name" as destination_country_name
            FROM export_tariff
			LEFT JOIN products ON products.id = export_tariff.product_id 
            LEFT JOIN destination_country ON destination_country.id = export_tariff.destination_country_id
            WHERE destination_country."name" ILIKE '{destination_country}' AND products."name" ILIKE '{product}' AND export_tariff.year > {results2[0][0]-6} AND export_tariff.year <= {results2[0][0]}
            ORDER BY products."name", destination_country."name", export_tariff.year
            """
        
        print(f"Paremeters: {destination_country} {product} {last_year}")

        cursor.execute(query3)
        results3 = cursor.fetchall()
                
        cursor.close()
        conn.close()
        if results3:
            narrative = []
            narrative.append(f"Tarif ekspor produk {product} ke {destination_country} dari 5 tahun terakhir adalah sebagai berikut:\n")
            for result in results3:
                export_tariff_id,product_id,destination_country_id,weighted_average_tariff,year, product_name, destination_country_name = result
                narrative.append(f"Tarif ekspor {product} ke negara {destination_country} pada tahun {year} sekitar {weighted_average_tariff} %")
            narrative.append(f"Selain itu, Logistic Performance Index {destination_country} sebesar {logistic_performance_index}\n")
            
            narrative = "\n".join(narrative)
        else:
            narrative = f"Data tidak ditemukan."
        return {
                "narrative": narrative,
                "attachment": None
            }
    def get_trade_representative(self, destination_country):
        """
        Retrieves the trend export yearly based on destination country and product.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query = f"""
            SELECT trade_representative.id as trade_representative_id,destination_country_id,trade_representative, organization, address, telephone, fax,email, website, destination_country."name" as destination_country_name 
            FROM trade_representative
            LEFT JOIN destination_country ON destination_country.id = trade_representative.destination_country_id
            WHERE destination_country."name" ILIKE '{destination_country}'
            """
        
        print(f"Paremeters: {destination_country}")

        cursor.execute(query)
        results = cursor.fetchall()
                
        cursor.close()
        conn.close()

        if results:
            narrative = []
            narrative.append(f"Berikut merupakan perwakilan perdagangan di {destination_country}\n")
            for result in results:
                (
                    trade_representative_id, 
                    destination_country_id, 
                    trade_representative, 
                    organization, 
                    address, 
                    telephone, 
                    fax, 
                    email, 
                    website, 
                    destination_country_name
                ) = result

                narrative.append(f"{trade_representative} – {destination_country_name}")
                narrative.append(f"Alamat\t: {address}")
                narrative.append(f"Telepon\t: {telephone}")
                narrative.append(f"Fax\t: {fax}")
                narrative.append(f"Email\t: {email}")
                narrative.append(f"Website\t: {website}\n")
                narrative.append(f"Organisasi\t: {organization}\n\n")

            narrative = "\n".join(narrative)
        else:
            narrative = f"Tidak ada data perwakilan dagang."

        return {
                "narrative": narrative,
                "attachment": None
            }
    def get_xmarket(self, destination_country,product):
        """
        Retrieves the trend export yearly based on destination country and product.
        """
        conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
        cursor = conn.cursor()
        query1 = f"""
            SELECT max(xmarket_analysis.year) as last_year
            FROM xmarket_analysis
			LEFT JOIN products ON products.id = xmarket_analysis.product_id 
            LEFT JOIN destination_country ON destination_country.id = xmarket_analysis.destination_country_id
            WHERE destination_country."name" ILIKE '{destination_country}' AND products."name" ILIKE '{product}'
            
            """
        
        print(f"Paremeters: {destination_country} {product}")

        cursor.execute(query1)
        results1 = cursor.fetchall()
        if results1:
            last_year = str(results1[0][0])

        query2 = f"""
            SELECT xmarket_analysis.id as xmarket_analysis_id,product_id,destination_country_id,rca,epd,xmarket, xmarket_analysis.year as last_year,products."name" as products_name, destination_country."name" as destination_country_name 
            FROM xmarket_analysis
            LEFT JOIN products ON products.id = xmarket_analysis.product_id 
            LEFT JOIN destination_country ON destination_country.id = xmarket_analysis.destination_country_id
            WHERE destination_country."name" ILIKE '{destination_country}' AND products."name" ILIKE '{product}' AND xmarket_analysis.year = '{last_year}'
            """
        
        print(f"Paremeters: {destination_country} {product} {last_year}")

        cursor.execute(query2)
        results2 = cursor.fetchall()
                
        cursor.close()
        conn.close()

        if results2:
            narrative = []
            xmarket_analysis_id,product_id,destination_country_id,rca,epd,xmarket, last_year, product_name, destination_country_name= results2[0]
            if rca>=1:
                narrative.append(f"Revealed Comparative Advantage (RCA) dengan nilai {rca} (RCA>=1) menunjukkan bahwa Indonesia memiliki keunggulan komparatif dalam ekspor {product} ke {destination_country}.")
            else:
                narrative.append(f"Revealed Comparative Advantage (RCA) dengan nilai {rca} (RCA<1)menunjukkan bahwa Indonesia tidak memiliki keunggulan komparatif dalam ekspor {product} ke {destination_country}.")
            narrative.append(f"Hasil Export Portfolio Diagram (EPD) yang menunjukkan bahwa {product} Indonesia berada dalam kategori {epd} di pasar {destination_country}, bersama dengan analisis X-Model yang menunjukkan {product} Indonesia sebagai {xmarket}.")
            narrative = "\n".join(narrative)
        else:
            narrative = f"Data tidak ditemukan."
        return narrative

    
    # def get_market_intelligence(self,product, destination_country):
    #     """
    #     Retrieves export recommendations based on the provided parameters
    #     """
    #     conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
    #     cursor = conn.cursor()
    #     query1 = """
    #             SELECT *
    #             FROM product
    #             WHERE product ILIKE %s
    #             LIMIT 1;
    #     """
    #     print(query1)
    #     print(f"Parameters: {product}")

    #     # Execute the query with the provided parameters
    #     cursor.execute(query1, (
    #         product
    #     ))
    #     results1 = cursor.fetchall()
    #     product_id,product_hs_code,product_name,product_description,product_weight = results1[0]

    #     query2 = """
    #             SELECT *
    #             FROM destination_country
    #             WHERE destination_country ILIKE %s
    #             LIMIT 1;
    #     """
    #     print(query2)
    #     print(f"Parameters: {destination_country}")

    #     # Execute the query with the provided parameters
    #     cursor.execute(query1, (
    #         destination_country
    #     ))
    #     results2 = cursor.fetchall()
        
    #     destination_country_id,destination_country_name,destination_country_geography,destination_country_demography,destination_country_gdp_percapita = results2[0]
    #     cursor.close()
    #     conn.close()
    #     print(results1.index)
    #     if results1 and results2:
    #         recommendations = []
    #         recommendations.append(
    #         f"{destination_country_name}. Jumlah penduduk {destination_country_name} sebesar {destination_country_demography} membuat {destination_country_name} menjadi pasar yang potensial. Dalam hal ekonomi, Produk Domestik Bruto (PDB) per kapita sebesar {destination_country_gdp_percapita}.\n\n"
    #         )
    #         recommendations.append(
    #         f"{i+1}. **Negara Tujuan: {destination_country}**\n"
    #             "---------------------------------------------------------------------------\n"
    #             f"**Profil Negara:**\n"
    #             f"{country_geography}. Jumlah penduduk {destination_country} sebesar {country_demographics} membuat {destination_country} menjadi pasar yang potensial. Dalam hal ekonomi, Produk Domestik Bruto (PDB) per kapita sebesar {gdp_per_capita}.\n\n"
    #             "**Deskripsi Produk:**\n"
    #             f"{deskripsi_produk}\n\n"
    #         )

    #         narrative = "\n".join(recommendations)
    #     else:
    #         narrative = "Tidak ada rekomendasi yang tersedia."


    #     return narrative
    
    # def get_export_recommendation(self,product, monthly_production_capacity, product_quality, business_entity_legality, 
    #                            business_field_licensing, finance_and_taxation, domicile_regency_city, nearest_airport_port):
    #     """
    #     Retrieves export recommendations based on the provided parameters from the 'kb_ekspor1' table.
    #     """
    #     conn = self.connect_db(settings.POSTGRE_CONNECTION_STR)
    #     cursor = conn.cursor()
    #     query = """
    #         SELECT 
    #             destination_country, 
    #             destination_country_regulations_requirements
    #         FROM kb_ekspor1
    #         WHERE product = %s
    #         AND monthly_production_capacity >= %s
    #         AND product_quality = %s
    #         AND business_entity_legality = %s
    #         AND business_field_licensing = %s
    #         AND finance_and_taxation = %s
    #         AND domicile_regency_city = %s
    #         AND nearest_airport_port = %s;
    #     """
    #     print(f"Parameters: {product}, {monthly_production_capacity}, {product_quality}, {business_entity_legality}, "
    #         f"{business_field_licensing}, {finance_and_taxation}, {domicile_regency_city}, {nearest_airport_port}")

    #     # Execute the query with the provided parameters
    #     cursor.execute(query, (
    #         product, 
    #         monthly_production_capacity, 
    #         product_quality, 
    #         business_entity_legality, 
    #         business_field_licensing, 
    #         finance_and_taxation, 
    #         domicile_regency_city, 
    #         nearest_airport_port
    #     ))
    #     results = cursor.fetchall()
    #     cursor.close()
    #     conn.close()

    #     if results:
    #         recommendations = []
    #         for result in results:
    #             destination_country, destination_country_regulations_requirements = result
    #             recommendations.append(
    #                 f"Recommended destination country: {destination_country}, "
    #                 f"Regulations: {destination_country_regulations_requirements}, "
    #             )
    #         narrative = "Inilah beberapa rekomendasi:\n" + "\n".join(recommendations)
    #     else:
    #         narrative = "Tidak ada rekomendasi yang tersedia."

    #     return narrative


