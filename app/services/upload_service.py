"""
Upload service for sprint summaries
"""

import json
import csv
import io
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.sprint_summary import SprintSummary
from app.schemas.sprint_summary import SprintSummaryCreate


class UploadService:
    """Upload service for processing sprint summaries"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_sprint_summary(
        self, 
        file_content: bytes, 
        filename: str, 
        file_size: int,
        sprint_id: str = None,
        title: str = None,
        uploaded_by: int = None
    ) -> SprintSummary:
        """Process uploaded sprint summary file"""
        
        # Parse file content based on extension
        raw_data = self._parse_file_content(file_content, filename)
        
        # Process the data into structured format
        processed_data = self._process_sprint_data(raw_data)
        
        # Generate sprint_id if not provided
        if not sprint_id:
            sprint_id = f"sprint_{filename.split('.')[0]}"
        
        # Create sprint summary record
        sprint_summary = SprintSummary(
            sprint_id=sprint_id,
            title=title or filename,
            file_name=filename,
            file_size=file_size,
            uploaded_by=uploaded_by,
            raw_data=raw_data,
            processed_data=processed_data,
            status="processed"
        )
        
        self.db.add(sprint_summary)
        self.db.commit()
        self.db.refresh(sprint_summary)
        
        return sprint_summary
    
    def _parse_file_content(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse file content based on file type"""
        try:
            if filename.endswith('.json'):
                return json.loads(content.decode('utf-8'))
            elif filename.endswith('.csv'):
                return self._parse_csv_content(content)
            elif filename.endswith('.txt'):
                return {"content": content.decode('utf-8')}
            else:
                raise ValueError(f"Unsupported file type: {filename}")
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}")
    
    def _parse_csv_content(self, content: bytes) -> Dict[str, Any]:
        """Parse CSV content into dictionary"""
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
        return {"rows": rows, "headers": list(rows[0].keys()) if rows else []}
    
    def _process_sprint_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw sprint data into structured format"""
        processed = {
            "summary": {},
            "metrics": {},
            "stories": [],
            "issues": []
        }
        
        # Basic processing - can be enhanced based on actual data structure
        if isinstance(raw_data, dict):
            if "content" in raw_data:
                # Text file processing
                processed["summary"]["description"] = raw_data["content"]
            elif "rows" in raw_data:
                # CSV processing
                processed["stories"] = raw_data["rows"]
            else:
                # JSON processing
                processed.update(raw_data)
        
        return processed
    
    def get_sprint_summary(self, summary_id: int, user_id: int) -> Optional[SprintSummary]:
        """Get a specific sprint summary"""
        return self.db.query(SprintSummary).filter(
            SprintSummary.id == summary_id,
            SprintSummary.uploaded_by == user_id
        ).first()
    
    def get_user_sprint_summaries(self, user_id: int, skip: int = 0, limit: int = 100) -> List[SprintSummary]:
        """Get user's sprint summaries"""
        return self.db.query(SprintSummary).filter(
            SprintSummary.uploaded_by == user_id
        ).offset(skip).limit(limit).all()
    
    def delete_sprint_summary(self, summary_id: int, user_id: int) -> bool:
        """Delete a sprint summary"""
        summary = self.get_sprint_summary(summary_id, user_id)
        if summary:
            self.db.delete(summary)
            self.db.commit()
            return True
        return False
