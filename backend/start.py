import uvicorn
import os
from dotenv import load_dotenv
import multiprocessing

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações do servidor
host = os.getenv("API_HOST", "0.0.0.0")
port = int(os.getenv("API_PORT", "8000"))
reload = os.getenv("DEBUG", "True").lower() == "true"

if __name__ == "__main__":
    print(f"Iniciando servidor em http://{host}:{port}")
    print("Pressione CTRL+C para parar o servidor")
    
    # Inicia o servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    ) 