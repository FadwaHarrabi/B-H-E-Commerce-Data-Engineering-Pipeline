from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
import json
from airflow import DAG
from datetime import datetime
hook=PostgresHook(
    postgres_conn_id='bhp_postgres'
)
def insert_data_department_table():
    with open ('/opt/airflow/Data/department.json','r') as f:
         data=json.load(f)
    
    conn=hook.get_conn()
    cursor=conn.cursor()
    for row in data:
         cursor.execute(
              "Insert into department(Code,Title,Url,ScrapedAt) values (%s,%s,%s,%s)",
              (row['Code'],row['DepartmentName'],row['url'],row['ScrapedAt'])
         )
    conn.commit()
    cursor.close()
    conn.close()
    print("Data inserted into department table successfully")
def insert_data_categories_table():
    with open('/opt/airflow/Data/categories.json','r') as f:
          data=json.load(f)
    conn=hook.get_conn()
    cursor=conn.cursor()
    for row in data:
         cursor.execute("Insert into categories (Code,Category,SubCategory,Url,DepartmentCode,ScrapedAt)" \
         "values(%s,%s,%s,%s,%s,%s)", (row['Code'],row['Category'],row['SubCategory'],row['url'],row['DepartmentCode'],row['ScrapedAt']))
    conn.commit()
    cursor.close()
    conn.close()
    print("Data inserted into categories table successfully")
def insert_data_subsubcategories_table():
     with open('/opt/airflow/Data/subsubcategory_group.json','r')  as f:
          data=json.load(f)
     conn=hook.get_conn()
     cursor=conn.cursor()
     for row in data:
          cursor.execute(
               "Insert into subsubcategories (Code,name,Url,SubcategoriesCode,ScrapedAt) "
                "values (%s,%s,%s,%s,%s)",
                (row['Code'],row['name'],row['url'],row['SubcategoriesCode'],row['ScrapedAt'])
          )
     conn.commit()
     cursor.close()
     conn.close()
     print("Data inserted into subsubcategories table successfully")
def insert_data_subcategories_table():
     with open('/opt/airflow/Data/subcategories_group.json','r')  as f:
          data=json.load(f)
     conn=hook.get_conn()
     cursor=conn.cursor()
     for row in data:
          cursor.execute(
               "Insert into subcategories (Code,name,Url,CategoriesCode,ScrapedAt) "
                "values (%s,%s,%s,%s,%s)",
                (row['Code'],row['name'],row['url'],row['CategoriesCode'],row['ScrapedAt'])
          )
     conn.commit()
     cursor.close()
     conn.close()
     print("Data inserted into subcategories table successfully")
def insert_data_Product_table():
     with open('/opt/airflow/Data/products.json','r')  as f:
          data=json.load(f)
     conn=hook.get_conn()
     cursor=conn.cursor()
     for row in data:
          cursor.execute(
               "Insert into Product (Code,category_id,subcategory_id,subsubcategory_id,image,name,reference" \
               ",price,initial_price,saved_price,stock_status,reviews,key_features,ScrapedAt) "
                "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (row['Code'],row['category_id'],row['subcategory_id'],row['subsubcategory_id'],row['image'],row['name'],row['reference'],row['price'],row['initial_price'],row['saved_price'],row['stock_status'],row['reviews'],row['key_features'],row['ScrapedAt'])
          )
     conn.commit()
     cursor.close()
     conn.close()
     print("Data inserted into products table successfully")
def insert_data_filters_table():
     with open('/opt/airflow/Data/filters.json','r')  as f:
          data=json.load(f)
     conn=hook.get_conn()
     cursor=conn.cursor()
     for row in data:
          cursor.execute(
   
               "Insert into filters (Code,category_code,subcategory_code,subsubcategory_code,filter,options,ScrapedAt)"
                "values (%s,%s,%s,%s,%s,%s,%s)",
                (row['Code'],row['category_code'],row['subcategory_code'],row['subsubcategory_code'],row['filter'],row['options'],row['ScrapedAt'])
          )
     conn.commit()
     cursor.close()
     conn.close()
     print("Data inserted into filters table successfully")
with DAG(
     dag_id='BronzeInsertionData',
     start_date=datetime(2026,9,5),
     schedule="@daily",
     catchup=False
) as dag:
     DepartmentData=PythonOperator(
         task_id="DepartmentData",
         python_callable=insert_data_department_table
     )
     CategoryData=PythonOperator(
             task_id="CategoryData",
             python_callable=insert_data_categories_table
     )
     SubCategoryData=PythonOperator(
                task_id="SubCategoryData",
                python_callable=insert_data_subcategories_table
      )
     SubSubCategoryData=PythonOperator(
                task_id="SubSubCategoryData",
                python_callable=insert_data_subsubcategories_table
      )
     ProductData=PythonOperator(
                task_id="ProductData",
                python_callable=insert_data_Product_table
      )
     FilterData=PythonOperator(
                task_id="FilterData",
                python_callable=insert_data_filters_table
      )
     DepartmentData >> CategoryData >> SubCategoryData >> SubSubCategoryData >> ProductData >> FilterData