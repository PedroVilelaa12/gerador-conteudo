import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def upload_to_s3(file_path: str, subfolder: str = "instagram") -> str:
    """
    Faz upload de um arquivo para o bucket S3 e retorna a URL pública HTTPS.
    Usa ACL 'public-read' apenas para a pasta 'instagram/'.
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-2")
    )

    bucket = os.getenv("AWS_BUCKET_NAME", "niceas-ia-content")
    file_name = os.path.basename(file_path)
    s3_key = f"{subfolder}/{file_name}"

    try:
        extra_args = {}
        if os.getenv("AWS_ALLOW_ACL", "false").lower() == "true":
            extra_args["ACL"] = "public-read"

        if extra_args:
            s3.upload_file(file_path, bucket, s3_key, ExtraArgs=extra_args)
        else:
            s3.upload_file(file_path, bucket, s3_key)
    except boto3.exceptions.S3UploadFailedError:
        raise

    region = os.getenv("AWS_REGION", "us-east-2")
    public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
    print(f"✅ Upload concluído: {public_url}")
    return public_url


if __name__ == "__main__":
    arquivo = r"C:\Users\Viana e Moura.VM210490\Downloads\2025-10-20-21-03-29.mp4"
    upload_to_s3(arquivo)