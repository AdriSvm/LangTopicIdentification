from app import create_app



if __name__ == '__main__':
    from waitress import serve
    app = create_app()
    serve(app,host='0.0.0.0',port=5000)
else:
    app = create_app()
