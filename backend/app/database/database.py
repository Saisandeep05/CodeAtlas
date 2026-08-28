import sqlite3
import json
from typing import Dict, Any, Optional
from config import ANALYZER_VERSION

class Database:
    def __init__(self, db_path: str = "codeatlas.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                repository_name TEXT,
                commit_hash TEXT,
                analyzer_version TEXT,
                status TEXT,
                analysis_duration REAL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_cache (
                repository_id INTEGER PRIMARY KEY,
                analyzer_version TEXT,
                graph_json TEXT,
                source_code_cache TEXT,
                file_tree_json TEXT,
                statistics_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(repository_id) REFERENCES repositories(id)
            )
        ''')

        self._migrate_columns(cursor)
        conn.commit()
        conn.close()

    def _migrate_columns(self, cursor):
        """Add missing columns to existing tables for backwards compatibility."""
        cursor.execute("PRAGMA table_info(repositories)")
        repo_cols = {row[1] for row in cursor.fetchall()}
        if "repository_name" not in repo_cols:
            cursor.execute("ALTER TABLE repositories ADD COLUMN repository_name TEXT")
        if "analysis_duration" not in repo_cols:
            cursor.execute("ALTER TABLE repositories ADD COLUMN analysis_duration REAL")
        if "analyzer_version" not in repo_cols:
            cursor.execute("ALTER TABLE repositories ADD COLUMN analyzer_version TEXT")

        cursor.execute("PRAGMA table_info(analysis_cache)")
        cache_cols = {row[1] for row in cursor.fetchall()}
        if "file_tree_json" not in cache_cols:
            cursor.execute("ALTER TABLE analysis_cache ADD COLUMN file_tree_json TEXT")
        if "statistics_json" not in cache_cols:
            cursor.execute("ALTER TABLE analysis_cache ADD COLUMN statistics_json TEXT")
        if "analyzer_version" not in cache_cols:
            cursor.execute("ALTER TABLE analysis_cache ADD COLUMN analyzer_version TEXT")

    def get_repo_by_url(self, repo_url: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM repositories WHERE url = ?', (repo_url,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_repo_by_id(self, repo_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM repositories WHERE id = ?', (repo_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def create_or_update_repo(
        self, repo_url: str, commit_hash: str,
        repository_name: str = None, analysis_duration: float = None,
        analyzer_version: str = ANALYZER_VERSION
    ) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM repositories WHERE url = ?', (repo_url,))
        row = cursor.fetchone()

        if row:
            repo_id = row[0]
            cursor.execute(
                '''UPDATE repositories
                   SET commit_hash = ?, analyzer_version = ?, status = ?, repository_name = ?,
                       analysis_duration = ?, analyzed_at = CURRENT_TIMESTAMP
                   WHERE id = ?''',
                (commit_hash, analyzer_version, 'analyzed', repository_name, analysis_duration, repo_id)
            )
        else:
            cursor.execute(
                '''INSERT INTO repositories
                   (url, commit_hash, analyzer_version, status, repository_name, analysis_duration)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (repo_url, commit_hash, analyzer_version, 'analyzed', repository_name, analysis_duration)
            )
            repo_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return repo_id

    def get_cached_graph(self, repo_id: int, current_version: str = ANALYZER_VERSION) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT graph_json, analyzer_version FROM analysis_cache WHERE repository_id = ?',
            (repo_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            version = row[1]
            if version and version != current_version:
                return None  # Version mismatch -> cache invalidation!
            return json.loads(row[0])
        return None

    def get_cached_source(self, repo_id: int) -> Optional[Dict[str, str]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT source_code_cache FROM analysis_cache WHERE repository_id = ?', (repo_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
        return None

    def get_cached_file_tree(self, repo_id: int) -> Optional[Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT file_tree_json FROM analysis_cache WHERE repository_id = ?', (repo_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
        return None

    def get_cached_statistics(self, repo_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT statistics_json FROM analysis_cache WHERE repository_id = ?', (repo_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
        return None

    def cache_analysis(
        self, repo_id: int, graph_data: Dict[str, Any],
        source_cache: Dict[str, str],
        file_tree: Any = None, statistics: Dict[str, Any] = None,
        analyzer_version: str = ANALYZER_VERSION
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO analysis_cache
            (repository_id, analyzer_version, graph_json, source_code_cache, file_tree_json, statistics_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            repo_id,
            analyzer_version,
            json.dumps(graph_data),
            json.dumps(source_cache),
            json.dumps(file_tree) if file_tree else None,
            json.dumps(statistics) if statistics else None
        ))
        conn.commit()
        conn.close()
