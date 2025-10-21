#!/usr/bin/env python3
"""
Modelos de Banco de Dados
Descrição: Modelos SQLAlchemy para o sistema de automação de conteúdo
Autor: Gerador de Conteúdo
Data: 2024
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class GeneratedContent(Base):
    """Modelo para conteúdo gerado por IA"""
    __tablename__ = 'generated_content'
    
    id = Column(String, primary_key=True)
    prompt = Column(Text, nullable=False)
    revised_prompt = Column(Text)
    size = Column(String(20))
    quality = Column(String(20))
    style = Column(String(20))
    filepath = Column(String(500))
    filename = Column(String(200))
    public_url = Column(String(500))
    status = Column(String(50), default='pending_approval')  # pending_approval, approved, rejected, published
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    
    # Relacionamentos
    publications = relationship("Publication", back_populates="content")

class Publication(Base):
    """Modelo para publicações em redes sociais"""
    __tablename__ = 'publications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String, ForeignKey('generated_content.id'), nullable=False)
    platform = Column(String(50), nullable=False)  # tiktok, instagram, linkedin
    platform_post_id = Column(String(200))
    custom_description = Column(Text)
    hashtags = Column(String(500))
    published_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='published')  # published, failed, deleted
    
    # Relacionamentos
    content = relationship("GeneratedContent", back_populates="publications")
    metrics = relationship("Metrics", back_populates="publication")

class Metrics(Base):
    """Modelo para métricas de posts"""
    __tablename__ = 'metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_id = Column(Integer, ForeignKey('publications.id'), nullable=False)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    collected_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)  # Dados brutos da API
    
    # Relacionamentos
    publication = relationship("Publication", back_populates="metrics")

class APIConfig(Base):
    """Modelo para configurações de API"""
    __tablename__ = 'api_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, unique=True)  # openai, tiktok, instagram, linkedin, aws
    api_key = Column(String(500))
    access_token = Column(String(500))
    refresh_token = Column(String(500))
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DatabaseManager:
    """Gerenciador do banco de dados"""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            # Usar SQLite por padrão
            database_url = "sqlite:///content_automation.db"
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Criar tabelas
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Obter sessão do banco"""
        return self.SessionLocal()
    
    def create_content(self, content_data: dict):
        """Criar novo conteúdo"""
        session = self.get_session()
        try:
            content = GeneratedContent(**content_data)
            session.add(content)
            session.commit()
            session.refresh(content)
            return content
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_content(self, content_id: str = None, status: str = None):
        """Obter conteúdo"""
        session = self.get_session()
        try:
            query = session.query(GeneratedContent)
            
            if content_id:
                query = query.filter(GeneratedContent.id == content_id)
            
            if status:
                query = query.filter(GeneratedContent.status == status)
            
            return query.all()
        finally:
            session.close()
    
    def update_content_status(self, content_id: str, status: str, **kwargs):
        """Atualizar status do conteúdo"""
        session = self.get_session()
        try:
            content = session.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
            if content:
                content.status = status
                for key, value in kwargs.items():
                    if hasattr(content, key):
                        setattr(content, key, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_publication(self, publication_data: dict):
        """Criar nova publicação"""
        session = self.get_session()
        try:
            publication = Publication(**publication_data)
            session.add(publication)
            session.commit()
            session.refresh(publication)
            return publication
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_publications(self, content_id: str = None, platform: str = None):
        """Obter publicações"""
        session = self.get_session()
        try:
            query = session.query(Publication)
            
            if content_id:
                query = query.filter(Publication.content_id == content_id)
            
            if platform:
                query = query.filter(Publication.platform == platform)
            
            return query.all()
        finally:
            session.close()
    
    def create_metrics(self, metrics_data: dict):
        """Criar métricas"""
        session = self.get_session()
        try:
            metrics = Metrics(**metrics_data)
            session.add(metrics)
            session.commit()
            session.refresh(metrics)
            return metrics
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_latest_metrics(self, publication_id: int):
        """Obter métricas mais recentes de uma publicação"""
        session = self.get_session()
        try:
            return session.query(Metrics).filter(
                Metrics.publication_id == publication_id
            ).order_by(Metrics.collected_at.desc()).first()
        finally:
            session.close()
    
    def save_api_config(self, platform: str, **config_data):
        """Salvar configuração de API"""
        session = self.get_session()
        try:
            config = session.query(APIConfig).filter(APIConfig.platform == platform).first()
            
            if config:
                # Atualizar configuração existente
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                config.updated_at = datetime.utcnow()
            else:
                # Criar nova configuração
                config_data['platform'] = platform
                config = APIConfig(**config_data)
                session.add(config)
            
            session.commit()
            return config
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_api_config(self, platform: str):
        """Obter configuração de API"""
        session = self.get_session()
        try:
            return session.query(APIConfig).filter(APIConfig.platform == platform).first()
        finally:
            session.close()
    
    def get_dashboard_stats(self):
        """Obter estatísticas para dashboard"""
        session = self.get_session()
        try:
            stats = {}
            
            # Contar conteúdo por status
            stats['total_content'] = session.query(GeneratedContent).count()
            stats['pending_content'] = session.query(GeneratedContent).filter(
                GeneratedContent.status == 'pending_approval'
            ).count()
            stats['approved_content'] = session.query(GeneratedContent).filter(
                GeneratedContent.status == 'approved'
            ).count()
            stats['published_content'] = session.query(GeneratedContent).filter(
                GeneratedContent.status == 'published'
            ).count()
            
            # Contar publicações
            stats['total_publications'] = session.query(Publication).count()
            
            # Métricas totais
            total_metrics = session.query(Metrics).all()
            stats['total_likes'] = sum(m.likes for m in total_metrics)
            stats['total_comments'] = sum(m.comments for m in total_metrics)
            stats['total_shares'] = sum(m.shares for m in total_metrics)
            stats['total_views'] = sum(m.views for m in total_metrics)
            
            return stats
        finally:
            session.close()

# Instância global do gerenciador de banco
db_manager = DatabaseManager()
