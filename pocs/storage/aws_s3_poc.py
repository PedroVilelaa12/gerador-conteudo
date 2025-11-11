#!/usr/bin/env python3
"""
POC - Armazenamento AWS S3
Descrição: POC para upload de arquivos para AWS S3
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import boto3
import logging
from typing import Any, Dict, Optional
from pocs.template_poc import POCTemplate

# Configurar logging
logger = logging.getLogger(__name__)


class AWSS3POC(POCTemplate):
    """POC para armazenamento em AWS S3"""
    
    def __init__(self):
        """Inicializar cliente S3"""
        super().__init__()
        self.name = "AWS S3 Storage POC"
        self.s3_client = None
        self.bucket_name = None
        self.region = None
        
        # Configurações
        self.access_key = None
        self.secret_key = None
    
    def setup(self) -> bool:
        """Configurar conexão com AWS S3"""
        try:
            logger.info("Configurando conexão com AWS S3...")
            
            # Carregar credenciais do ambiente
            self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
            self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            self.bucket_name = os.getenv('S3_BUCKET_NAME')
            self.region = os.getenv('AWS_REGION', 'us-east-1')
            
            if not self.access_key:
                logger.error("AWS_ACCESS_KEY_ID não encontrado nas variáveis de ambiente")
                return False
            
            if not self.secret_key:
                logger.error("AWS_SECRET_ACCESS_KEY não encontrado nas variáveis de ambiente")
                return False
            
            if not self.bucket_name:
                logger.warning("S3_BUCKET_NAME não encontrado nas variáveis de ambiente. S3 será desabilitado.")
                return False
            
            # Verificar se é um placeholder
            if 'seu-bucket-s3-aqui' in self.bucket_name.lower() or 'example' in self.bucket_name.lower():
                logger.warning(f"Bucket '{self.bucket_name}' parece ser um placeholder. Configure um bucket real no arquivo .env")
                return False
            
            # Criar cliente S3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            # Verificar se o bucket existe
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' encontrado")
            except Exception as e:
                # Se for um placeholder ou bucket não encontrado, não é crítico
                if 'seu-bucket-s3-aqui' in self.bucket_name.lower() or 'example' in self.bucket_name.lower():
                    logger.warning(f"Bucket '{self.bucket_name}' parece ser um placeholder. Configure um bucket real no arquivo .env")
                    return False
                elif '403' in str(e) or 'Forbidden' in str(e):
                    logger.warning(f"Acesso negado ao bucket '{self.bucket_name}'. Verifique permissões e credenciais AWS.")
                    return False
                else:
                    logger.error(f"Erro ao acessar bucket '{self.bucket_name}': {e}")
                    return False
            
            logger.info("Configuração do S3 concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração do S3: {e}")
            return False
    
    def upload_file(self, file_path: str, s3_key: str, content_type: str = None, make_public: bool = True) -> Dict[str, Any]:
        """Upload de arquivo para S3"""
        try:
            logger.info(f"Fazendo upload de {file_path} para S3...")
            
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "message": f"Arquivo não encontrado: {file_path}",
                    "data": {}
                }
            
            # Configurações do upload
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            if make_public:
                extra_args['ACL'] = 'public-read'
            
            # Fazer upload
            self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Gerar URL pública
            public_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Upload concluído: {public_url}")
            return {
                "status": "success",
                "message": "Arquivo enviado com sucesso",
                "data": {
                    "s3_key": s3_key,
                    "public_url": public_url,
                    "bucket": self.bucket_name,
                    "file_size": os.path.getsize(file_path)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def upload_bytes(self, data: bytes, s3_key: str, content_type: str = None, make_public: bool = True) -> Dict[str, Any]:
        """Upload de dados em bytes para S3"""
        try:
            logger.info(f"Fazendo upload de {len(data)} bytes para S3...")
            
            # Configurações do upload
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            if make_public:
                extra_args['ACL'] = 'public-read'
            
            # Fazer upload
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=data,
                **extra_args
            )
            
            # Gerar URL pública
            public_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Upload concluído: {public_url}")
            return {
                "status": "success",
                "message": "Dados enviados com sucesso",
                "data": {
                    "s3_key": s3_key,
                    "public_url": public_url,
                    "bucket": self.bucket_name,
                    "data_size": len(data)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def list_files(self, prefix: str = "") -> Dict[str, Any]:
        """Listar arquivos no bucket"""
        try:
            logger.info(f"Listando arquivos com prefixo: {prefix}")
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        "key": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'],
                        "url": f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{obj['Key']}"
                    })
            
            return {
                "status": "success",
                "message": f"Encontrados {len(files)} arquivos",
                "data": {
                    "files": files,
                    "count": len(files)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def delete_file(self, s3_key: str) -> Dict[str, Any]:
        """Deletar arquivo do S3"""
        try:
            logger.info(f"Deletando arquivo: {s3_key}")
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                "status": "success",
                "message": "Arquivo deletado com sucesso",
                "data": {"deleted_key": s3_key}
            }
            
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def run(self) -> Dict[str, Any]:
        """Executar teste de upload"""
        try:
            logger.info("Executando teste de upload para S3...")
            
            # Criar arquivo de teste
            test_content = "Este é um arquivo de teste para upload no S3"
            test_filename = "test_upload.txt"
            
            # Salvar arquivo temporário
            with open(test_filename, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # Upload do arquivo
            s3_key = f"test/{test_filename}"
            result = self.upload_file(
                test_filename, 
                s3_key, 
                content_type="text/plain"
            )
            
            # Limpar arquivo temporário
            if os.path.exists(test_filename):
                os.remove(test_filename)
            
            if result["status"] == "success":
                # Listar arquivos para verificar
                list_result = self.list_files("test/")
                result["data"]["list_result"] = list_result["data"]
                
                logger.info("Teste de upload concluído com sucesso")
                return result
            else:
                logger.error(f"Falha no teste: {result['message']}")
                return result
            
        except Exception as e:
            logger.error(f"Erro na execução: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def cleanup(self):
        """Limpar recursos"""
        try:
            logger.info("Limpando recursos do S3...")
            # Aqui você poderia limpar arquivos temporários, etc.
            logger.info("Limpeza do S3 concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = AWSS3POC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração do S3")
            return
        
        result = poc.run()
        
        print(f"\nResultado da POC - AWS S3 Storage:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success' and 'data' in result:
            print(f"\nDetalhes do upload:")
            print(f"  S3 Key: {result['data'].get('s3_key', 'N/A')}")
            print(f"  URL Pública: {result['data'].get('public_url', 'N/A')}")
            print(f"  Bucket: {result['data'].get('bucket', 'N/A')}")
            print(f"  Tamanho: {result['data'].get('file_size', 'N/A')} bytes")
            
            if 'list_result' in result['data']:
                print(f"  Arquivos no bucket: {result['data']['list_result'].get('count', 0)}")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()
