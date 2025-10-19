from .connection import db_connection
import torch
ALLOWED_ROLES = ['admin', 'operator', 'engineer']

def add_user(name:str,role:str,embedding:torch.Tensor):
        if role not in ALLOWED_ROLES:
            raise ValueError(f"Invalid role '{role}'. Allowed roles: {ALLOWED_ROLES}")
    

        try:
            conn=db_connection()
            cur = conn.cursor()
            

           
            sql_insert = "INSERT INTO users (name, role, created_at) VALUES (%s, %s, NOW()) RETURNING id;"
            cur.execute(sql_insert, (f"{name}", f"{role}"))
           
            # Fetch the new user's ID
            user_id = cur.fetchone()[0]
           
            print("A new user successfully added!")
            
            # Convert torch tensor to list (Postgres expects a Python list for double precision[])
            if isinstance(embedding, torch.Tensor):
                embedding_list = embedding.tolist()
            else:
                embedding_list = embedding  # assume already list

            # Insert embedding linked to user_id
            sql_insert_embedding = """
                INSERT INTO speaker_embeddings (user_id, embedding, created_at)
                VALUES (%s, %s, NOW());
            """
            cur.execute(sql_insert_embedding, (user_id, embedding_list))

            
            conn.commit()
            print(f"✅ User '{name}' added with embedding!")

        except Exception as e: # Catching a general exception
            print(f"An unexpected error occurred: {e}")
        
        finally:
             if conn:
                  cur.close()
                  conn.close()
             


def delete_user(user_id:int):
     
        try:
            conn=db_connection()
            cur = conn.cursor()
            

       
            sql_insert = f"DELETE FROM users WHERE id = {user_id};"
            cur.execute(sql_insert)
            conn.commit()
            print(f"✅ User  deleted successfully!")

        except Exception as e: # Catching a general exception
            print(f"An unexpected error occurred: {e}")
        finally:
             if conn:
                  cur.close()
                  conn.close()
             

        






def get_all_embeddings():
     try:
            conn=db_connection()
            cur = conn.cursor()
          
            sql_insert = "select embedding,user_id from speaker_embeddings;"
            cur.execute(sql_insert)
            # Fetch all results
            data = cur.fetchall()
            
            print(f"{len(data)} embeddings fetched correctly from db!")
            
            
            return data

     except Exception as e: # Catching a general exception
            print(f"An unexpected error occurred: {e}")
     finally:
             if conn:
                  cur.close()
                  conn.close()
def get_user_name(user_id):
     try:
          conn=db_connection()
          cur = conn.cursor()
          sql_insert = f"select name,role from users where id={user_id};"
          cur.execute(sql_insert)
            # Fetch all results
          data = cur.fetchall()
          if data:
            print("the user who is speaking found successfully!")
            return data
          print(f"the user with {user_id} is not found in db!")
     except Exception as e:
            print(f"An unexpected error occurred: {e}")
     finally:
             if conn:
                  cur.close()
                  conn.close()



def add_user_query(user_id,query_type,content):
    
    try:
        conn=db_connection()
        cur = conn.cursor()
        

        # Example INSERT query
        sql_insert = "INSERT INTO user_queries (user_id, type, content, status, created_at) VALUES (%s, %s,%s,%s,NOW())"
        cur.execute(sql_insert, (f"{user_id}", f"{query_type}",f"{content}","pending",))
        
        print("user query saved in db successfully!")
        
        conn.commit()
    
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
    
    finally:
             if conn:
                  cur.close()
                  conn.close()


def update_user_query(user_id,reg_model_pred=None,class_model_pred=None,status="executed",llm_response=None):
    
    try:
        conn=db_connection()
        cur = conn.cursor()
        

        # Example update query
        sql_update = """
        UPDATE user_queries
        SET status = %s,
            updated_at = NOW(),
            classification_model_response = %s,
            regression_model_response = %s,
            overall_llm_response=%s
        WHERE user_id = %s AND status = 'pending';
        """

        cur.execute(sql_update, (status,class_model_pred,reg_model_pred ,llm_response,user_id))

        
        print("user query updated in db successfully!")
        
        conn.commit()
    
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
    
    finally:
             if conn:
                  cur.close()
                  conn.close()




if __name__ =='__main__':
    # add_user("raheem",'admin',torch.tensor([0.01, 0.02, -0.03, 0.04, 0.05]))   
    # get_all_embeddings()


    update_user_query(8)

    