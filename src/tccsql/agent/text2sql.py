from __future__ import annotations
import re
from dataclasses import dataclass
from tccsql.llm import Message
from tccsql.database.safety import validate_readonly_sql
SYSTEM="Você é um agente text-to-SQL PostgreSQL. Responda somente com uma única consulta SELECT ou WITH terminada em SELECT. Não explique."
@dataclass
class Attempt: sql:str|None; response:object; validation_error:str|None
def extract_sql(text):
 match=re.search(r"```(?:sql)?\s*(.*?)```",text,re.I|re.S); return (match.group(1) if match else text).strip().rstrip(";")
class TextToSQLAgent:
 def __init__(self,provider,model_config): self.provider,self.model_config=provider,model_config
 def attempt(self,question,context,feedback=None):
  prompt=f"ESQUEMA:\n{context}\n\nPERGUNTA:\n{question}\nSQL:"
  messages=[Message("system",SYSTEM),Message("user",prompt)]
  if feedback: messages.append(Message("user",f"A tentativa anterior falhou tecnicamente: {feedback}. Corrija e responda somente SQL."))
  response=self.provider.generate(messages,self.model_config); candidate=extract_sql(response.text)
  try:return Attempt(validate_readonly_sql(candidate),response,None)
  except Exception as error:return Attempt(None,response,str(error))
