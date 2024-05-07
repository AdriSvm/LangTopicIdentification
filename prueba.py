import requests
import json

url = "http://127.0.0.1:5000/segmenttopics"

payload = json.dumps({
'text': '''
    El Consejo General del Poder Judicial encara un nuevo frente de tensión con la vista puesta en las elecciones que se celebrarán el próximo mes de noviembre para designar a los integrantes de las salas de gobierno en el Tribunal Supremo, la Audiencia Nacional y los 17 tribunales superiores de justicia, unos puestos clave para la organización y funcionamiento del poder judicial en cada territorio. Desde las asociaciones minoritarias y sectores progresistas del Consejo se denuncia lo califican de 'maniobra' de los conservadores para abortar los planes en los que ya se trabajaba para introducir el voto telemático en el proceso, superando el sistema actual de voto presencial o por correo que según estas fuentes viene facilitando una posición de dominio por parte de la mayoritaria Asociación Profesional de la Magistratura en la mayoría de los órganos. El asunto saldrá previsiblemente a colación en la Comisión Permanente que se celebra este jueves y que incluye un punto sobre la cuestión. En la actualidad, y como la elección se produce en día laborable, es común y viene siendo aceptado que un juez de Soria, por ejemplo, evite trasladarse a la sede de su TSJ a Burgos -o uno de Huelva a la sede del TSJ en Granada- para emitir su voto presencial. Para el que se hace por correo, muchas veces se delega en otro compañero de la asociación que se pasa por los despachos para recopilar varios votos, y a quien se entrega el sobre y la fotocopia del carnet profesional para facilitar la gestión, perdiendo desde entonces el control sobre el recorrido del voto que llega finalmente a la urna. Este sistema de delegación, aunque admitido, no garantiza la integridad y el anonimato señalan las fuentes consultadas, que explican se trata de elegir en listas abiertas que permiten que, aunque un juez sea miembro de una asociación en concreto, pueda apoyar a candidatos de otras organizaciones o a compañeros independientes. La idea de impulsar el voto telemático ante las elecciones de este año fue propuesto al Consejo General del Poder Judicial por el Foro Judicial Independiente y Juezas y Jueces para la Democracia, con el apoyo también de la segunda asociación con más apoyos, la Francisco de Vitoria.
'''
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxNDU1NDg5NiwianRpIjoiMGZhZTgyYmMtYzA3Ni00ODQ4LWFmMDgtNWI2MDJhZDUyZjUwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkcmlhc3ZtIiwibmJmIjoxNzE0NTU0ODk2LCJjc3JmIjoiZmFmYWY5MTktMGU3NC00NmVjLTg5MjUtOTk5MzI5OTViZjlhIiwiZXhwIjoxNzE0NTU1Nzk2fQ.VUj1sGt7Rhn3XE009OsB3_O7VspdOhNpR9XL5wfGLwU'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
