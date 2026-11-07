import sys


def main():
    """
    Função principal de entrada que serve como ponto de partida da aplicação.
    Exibe uma mensagem inicial simples de boas-vindas ou inicia o servidor da API.
    """
    if len(sys.argv) > 1 and sys.argv[1] in ("--api", "serve", "api"):
        import uvicorn
        uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("Hello from Vox AI! Para iniciar a API: python main.py --api")


if __name__ == "__main__":
    main()

