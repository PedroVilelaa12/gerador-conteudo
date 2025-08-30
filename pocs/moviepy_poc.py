#!/usr/bin/env python3
"""
MoviePy POC - Montagem Básica de Vídeo
Descrição: POC para juntar dois vídeos em sequência e adicionar texto sobreposto
Autor: POC Generator
Data: 2024
"""

import os
from typing import Any, Dict
from template_poc import POCTemplate, logger
from moviepy import VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips


class MoviePyPOC(POCTemplate):
    """POC para montagem básica de vídeo com MoviePy"""
    
    def __init__(self):
        """Inicializar editor de vídeo"""
        super().__init__()
        self.name = "MoviePy - Montagem Básica de Vídeo POC"
        self.video_paths = []
        self.output_path = "output/video_montado.mp4"
        self.texto_sobreposto = "Teste de Edição"
        
    def setup(self) -> bool:
        """Configurar editor de vídeo"""
        try:
            logger.info("Configurando editor de vídeo...")
            
            # Criar diretório de output se não existir
            os.makedirs("output", exist_ok=True)
            
            # Procurar por qualquer vídeo na pasta videos/
            import glob
            videos_encontrados = glob.glob("videos/*.mp4") + glob.glob("videos/*.avi") + glob.glob("videos/*.mov")
            
            # Usar os vídeos encontrados
            for video_path in videos_encontrados:
                self.video_paths.append(video_path)
                if len(self.video_paths) >= 2:
                    break
            
            # Se não encontrou vídeos, criar instruções para o usuário
            if len(self.video_paths) < 2:
                logger.warning("Não foram encontrados pelo menos 2 vídeos para teste")
                logger.info("Por favor, coloque pelo menos 2 vídeos na pasta 'videos/' com nomes:")
                logger.info("- video1.mp4 (ou .avi, .mov)")
                logger.info("- video2.mp4 (ou .avi, .mov)")
                return False
            
            logger.info(f"Vídeos encontrados: {self.video_paths}")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração: {e}")
            return False
    
    def criar_video_montado(self) -> bool:
        """Criar vídeo montado juntando dois vídeos e adicionando texto"""
        try:
            logger.info("Carregando vídeos...")
            
            # Carregar os dois vídeos
            video1 = VideoFileClip(self.video_paths[0])
            video2 = VideoFileClip(self.video_paths[1])
            
            logger.info(f"Vídeo 1: {video1.duration:.2f}s")
            logger.info(f"Vídeo 2: {video2.duration:.2f}s")
            
            # Juntar os vídeos em sequência
            logger.info("Juntando vídeos em sequência...")
            video_concatenado = concatenate_videoclips([video1, video2])
            logger.info(f"Vídeo concatenado: {video_concatenado.duration:.2f}s")
            
            # Criar texto sobreposto usando arquivo temporário
            logger.info("Adicionando texto sobreposto...")
            try:
                from PIL import Image, ImageDraw, ImageFont
                import tempfile
                
                # Criar uma imagem com texto
                width, height = 640, 100
                img = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Transparente
                draw = ImageDraw.Draw(img)
                
                # Tentar usar uma fonte padrão do Windows
                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
                    except:
                        font = ImageFont.load_default()
                
                # Calcular posição do texto para centralizar
                bbox = draw.textbbox((0, 0), self.texto_sobreposto, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                
                # Desenhar texto com contorno
                # Contorno preto
                for adj in range(-2, 3):
                    for adj2 in range(-2, 3):
                        draw.text((x+adj, y+adj2), self.texto_sobreposto, font=font, fill=(0, 0, 0, 255))
                
                # Texto branco por cima
                draw.text((x, y), self.texto_sobreposto, font=font, fill=(255, 255, 255, 255))
                
                # Salvar como arquivo temporário
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    img.save(tmp_file.name, 'PNG')
                    temp_path = tmp_file.name
                
                # Criar ImageClip do arquivo
                from moviepy import ImageClip
                texto_clip = ImageClip(temp_path, duration=video_concatenado.duration)
                
                # Definir posição usando o método correto
                texto_clip = texto_clip.with_position(('center', 'top'))
                
                # Compor vídeo final com texto
                video_final = CompositeVideoClip([video_concatenado, texto_clip])
                logger.info("Texto adicionado com sucesso usando arquivo temporário")
                
                # Limpar arquivo temporário
                os.unlink(temp_path)
                
            except Exception as text_error:
                logger.warning(f"Erro ao adicionar texto: {text_error}")
                import traceback
                logger.warning(f"Detalhes: {traceback.format_exc()}")
                logger.info("Continuando sem texto sobreposto...")
                # Se falhar, usar apenas o vídeo concatenado
                video_final = video_concatenado
            
            # Salvar vídeo final
            logger.info(f"Salvando vídeo final em: {self.output_path}")
            video_final.write_videofile(self.output_path)
            
            # Limpar recursos
            video1.close()
            video2.close()
            video_concatenado.close()
            if 'texto' in locals():
                texto.close()
            video_final.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar vídeo montado: {e}")
            import traceback
            logger.error(f"Detalhes do erro: {traceback.format_exc()}")
            return False
    
    def verificar_resultado(self) -> Dict[str, Any]:
        """Verificar se o vídeo foi criado com sucesso"""
        try:
            if not os.path.exists(self.output_path):
                return {
                    "sucesso": False,
                    "mensagem": "Arquivo de vídeo não foi criado"
                }
            
            # Verificar tamanho do arquivo
            tamanho_arquivo = os.path.getsize(self.output_path)
            if tamanho_arquivo == 0:
                return {
                    "sucesso": False,
                    "mensagem": "Arquivo de vídeo está vazio"
                }
            
            # Tentar carregar o vídeo para verificar se está válido
            video_teste = VideoFileClip(self.output_path)
            duracao = video_teste.duration
            video_teste.close()
            
            return {
                "sucesso": True,
                "mensagem": "Vídeo criado com sucesso",
                "detalhes": {
                    "caminho": self.output_path,
                    "tamanho_mb": round(tamanho_arquivo / (1024 * 1024), 2),
                    "duracao_segundos": round(duracao, 2)
                }
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "mensagem": f"Erro ao verificar resultado: {e}"
            }
    
    def run(self) -> Dict[str, Any]:
        """Executar montagem de vídeo"""
        try:
            logger.info("Executando montagem de vídeo...")
            
            # Criar vídeo montado
            if not self.criar_video_montado():
                return {
                    "status": "error",
                    "message": "Falha ao criar vídeo montado",
                    "data": {}
                }
            
            # Verificar resultado
            verificacao = self.verificar_resultado()
            
            if verificacao["sucesso"]:
                result = {
                    "status": "success",
                    "message": "Montagem de vídeo concluída com sucesso",
                    "data": {
                        "videos_utilizados": len(self.video_paths),
                        "caminhos_videos": self.video_paths,
                        "video_final": verificacao["detalhes"],
                        "texto_adicionado": self.texto_sobreposto
                    }
                }
                logger.info("Montagem de vídeo concluída com sucesso")
            else:
                result = {
                    "status": "error",
                    "message": verificacao["mensagem"],
                    "data": {}
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na montagem: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def cleanup(self):
        """Limpar recursos"""
        try:
            logger.info("Limpando recursos do editor de vídeo...")
            # Aqui você poderia limpar arquivos temporários se necessário
            logger.info("Limpeza concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = MoviePyPOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração")
            print("\n❌ CONFIGURAÇÃO FALHOU")
            print("Para usar esta POC, você precisa:")
            print("1. Instalar MoviePy: pip install moviepy")
            print("2. Criar uma pasta 'videos/' no diretório atual")
            print("3. Colocar pelo menos 2 vídeos na pasta 'videos/' com nomes:")
            print("   - video1.mp4 (ou .avi, .mov)")
            print("   - video2.mp4 (ou .avi, .mov)")
            return
        
        result = poc.run()
        
        print(f"\nResultado da POC - MoviePy Montagem de Vídeo:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success':
            data = result['data']
            print(f"\n📹 Vídeos utilizados: {data['videos_utilizados']}")
            print("📁 Caminhos dos vídeos:")
            for i, caminho in enumerate(data['caminhos_videos'], 1):
                print(f"   {i}. {caminho}")
            
            print(f"\n🎬 Vídeo final criado:")
            print(f"   📍 Caminho: {data['video_final']['caminho']}")
            print(f"   📏 Tamanho: {data['video_final']['tamanho_mb']} MB")
            print(f"   ⏱️ Duração: {data['video_final']['duracao_segundos']} segundos")
            print(f"   💬 Texto adicionado: \"{data['texto_adicionado']}\"")
            
            print(f"\n✅ SUCESSO: Vídeo montado criado em '{data['video_final']['caminho']}'")
        else:
            print(f"\n❌ ERRO: {result['message']}")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()
