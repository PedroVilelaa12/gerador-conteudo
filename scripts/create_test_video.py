#!/usr/bin/env python3
"""
Script para criar um vídeo de teste simples
Requer ffmpeg instalado no sistema
"""

import os
import subprocess
import sys
from pathlib import Path


def check_ffmpeg():
    """Verificar se ffmpeg está instalado"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def create_test_video(output_path: str = "test_video.mp4", duration: int = 10):
    """
    Criar um vídeo de teste usando ffmpeg
    
    Args:
        output_path: Caminho para salvar o vídeo
        duration: Duração do vídeo em segundos
    """
    
    if not check_ffmpeg():
        print("ERRO: FFmpeg não encontrado!")
        print("   Instale o FFmpeg:")
        print("   - Windows: https://ffmpeg.org/download.html")
        print("   - ou use: winget install ffmpeg")
        return False
    
    try:
        # Comando para criar um vídeo de teste com:
        # - Fundo colorido animado
        # - Texto sobreposto
        # - Duração especificada
        # - Formato adequado para redes sociais (9:16)
        
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'color=c=blue:size=1080x1920:duration={duration}:rate=30',
            '-f', 'lavfi', 
            '-i', f'color=c=red:size=1080x1920:duration={duration}:rate=30',
            '-filter_complex',
            f'[0:v][1:v]blend=all_mode=multiply:all_opacity=0.5[bg];'
            f'[bg]drawtext=text=\'TESTE DE UPLOAD\\nVIDEO AUTOMATICO\\n{duration}s\':'
            f'fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:'
            f'shadowcolor=black:shadowx=2:shadowy=2',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            '-y',  # Sobrescrever arquivo se existir
            output_path
        ]
        
        print(f"Criando vídeo de teste: {output_path}")
        print(f"   Duração: {duration} segundos")
        print(f"   Resolução: 1080x1920 (9:16)")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"OK: Vídeo criado com sucesso!")
            print(f"   Arquivo: {os.path.abspath(output_path)}")
            print(f"   Tamanho: {file_size:.1f} MB")
            return True
        else:
            print(f"ERRO ao criar vídeo:")
            print(f"   {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERRO inesperado: {e}")
        return False


def main():
    """Função principal"""
    print("GERADOR DE VÍDEO DE TESTE")
    print("=" * 40)
    
    # Diretório de saída
    output_dir = Path(__file__).parent.parent / "test_media"
    output_dir.mkdir(exist_ok=True)
    
    # Criar vídeos de teste para diferentes plataformas
    videos = [
        {
            "name": "tiktok_test.mp4",
            "duration": 15,
            "description": "TikTok (15s, 9:16)"
        },
        {
            "name": "instagram_test.mp4", 
            "duration": 30,
            "description": "Instagram Reels (30s, 9:16)"
        }
    ]
    
    success_count = 0
    
    for video in videos:
        output_path = output_dir / video["name"]
        print(f"\nCriando {video['description']}...")
        
        if create_test_video(str(output_path), video["duration"]):
            success_count += 1
        else:
            print(f"   Falha ao criar {video['name']}")
    
    print(f"\nRESUMO:")
    print(f"   Vídeos criados: {success_count}/{len(videos)}")
    
    if success_count > 0:
        print(f"\nVídeos salvos em: {output_dir.absolute()}")
        print("\nPRÓXIMOS PASSOS:")
        print("   1. Configure o arquivo .env com as credenciais das APIs")
        print("   2. Para Instagram: hospede um vídeo publicamente e configure TEST_VIDEO_URL")
        print("   3. Configure TEST_VIDEO_PATH no .env apontando para um dos vídeos criados")
        print("   4. Execute: python scripts/test_social_apis.py")
    
    return success_count > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
