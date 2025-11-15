"""
Dashboard utilities for generating prediction statistics
"""
from datetime import datetime, timedelta
from collections import Counter
from .models import db, Prediction, Patient

def get_dashboard_stats():
    """Get overall system statistics"""
    stats = {
        'total_predictions': Prediction.query.count(),
        'total_patients': Patient.query.count(),
        'predictions_today': Prediction.query.filter(
            Prediction.created_at >= datetime.utcnow().date()
        ).count(),
        'recent_predictions': Prediction.query.order_by(
            Prediction.created_at.desc()
        ).limit(5).all()
    }
    
    # Get disease distribution
    all_predictions = Prediction.query.with_entities(Prediction.prediction).all()
    disease_counts = Counter(p[0] for p in all_predictions)
    stats['disease_distribution'] = dict(disease_counts.most_common(5))
    
    # Get weekly prediction trend
    week_ago = datetime.utcnow() - timedelta(days=7)
    daily_counts = db.session.query(
        db.func.date(Prediction.created_at).label('date'),
        db.func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= week_ago
    ).group_by(
        db.func.date(Prediction.created_at)
    ).order_by('date').all()
    
    stats['weekly_trend'] = {
        str(day.date): count for day, count in daily_counts
    }
    
    return stats