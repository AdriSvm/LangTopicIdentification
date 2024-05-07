
# LangChainTopicSegmentation

Flask API diseñada para implementar un identificador de topicos en el entorno de los telediarios. Especificamente para dado una transcripción de un telenoticias, obtener cada noticia mencionada y clasificada segun el topico de lo que habla.




## API Reference

#### Register

```http
  GET /register
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `username` | `string` | **Required**. Your username |
| `password` | `string` | **Required**. Your password |

##### Registers your username and password for future access

#### Log in

```http
  GET /login
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `username` | `string` | **Required**. Your username |
| `password` | `string` | **Required**. Your password |
| `OPENAI_API_KEY` | `string` | Your OPENAI_API_KEY |

#### The main endpoint to separate and identify the topic

```http
  POST /segmenttopics
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `text` | `string` | **Required**. The whole text to be identified |
| `parse` | `string` | **Required**. The level of parsing needed: CATEGORY/TOPIC/SUBTOPIC |

##### The parse type is essential for getting more concise or more general joins of news, CATEGORY will refer to politics/sports/etc, topic is a more concise like Political Elections Procedure, and subtopic even more concise like Catalan Elections Scandal


## Deployment

Will not address how to deploy a Flask API, but simply clone the repository, fill config.json and deploy it in your favorite waitress, gunicorn, etc, platform.



## Badges

Add badges from somewhere like: [shields.io](https://shields.io/)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)


## Authors

- [@AdriSvm](https://github.com/AdriSvm)

