"""
Numpy serializer utilities for JSON compatibility
Handles ObjectId, numpy types, datetime, and NaN values
"""
import json
import numpy as np
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Union, Dict, List
from bson import ObjectId

def convert_numpy_types(data: Any) -> Any:
    """
    Convert numpy types, ObjectId, datetime, and NaN values to JSON-serializable types
    
    Args:
        data: Any data structure (dict, list, scalar)
        
    Returns:
        JSON-serializable data structure
    """
    # Handle ObjectId first (before dict check)
    if isinstance(data, ObjectId):
        return str(data)
    
    if isinstance(data, dict):
        return {key: convert_numpy_types(value) for key, value in data.items()}
    
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    
    elif isinstance(data, np.integer):
        return int(data)
    
    elif isinstance(data, np.floating):
        # Handle NaN and infinity values
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    
    elif isinstance(data, np.ndarray):
        return data.tolist()
    
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    
    elif isinstance(data, Decimal):
        return float(data)
    
    elif pd.isna(data):
        return None
    
    elif hasattr(data, '__dict__'):
        # Handle other custom objects
        return str(data)
    
    else:
        return data

def safe_json_dumps(data: Any, **kwargs) -> str:
    """
    Safely serialize data to JSON string
    
    Args:
        data: Data to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string
    """
    # Convert numpy types first
    safe_data = convert_numpy_types(data)
    
    # Default JSON encoder settings
    default_kwargs = {
        'ensure_ascii': False,
        'separators': (',', ':'),
        'default': str  # Fallback for any remaining non-serializable types
    }
    default_kwargs.update(kwargs)
    
    return json.dumps(safe_data, **default_kwargs)

def clean_dataframe_for_json(df: pd.DataFrame) -> List[Dict]:
    """
    Clean DataFrame for JSON serialization
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        List of dictionaries with cleaned data
    """
    # Replace NaN values with None
    df_clean = df.replace({np.nan: None, np.inf: None, -np.inf: None})
    
    # Convert to dict and clean types
    records = df_clean.to_dict('records')
    return convert_numpy_types(records)