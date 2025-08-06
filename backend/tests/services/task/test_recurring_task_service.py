"""
Tests for the recurring task service.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.task.recurring_task_service import RecurringTaskService, RecurrenceType


class TestRecurringTaskService:
    """Test cases for RecurringTaskService."""
    
    def test_parse_simple_patterns(self):
        """Test parsing of simple recurrence patterns."""
        service = RecurringTaskService(None)  # No DB needed for pattern parsing
        
        # Test daily patterns
        result = service.parse_recurrence_pattern("daily")
        assert result["type"] == RecurrenceType.DAILY
        assert result["interval"] == 1
        
        result = service.parse_recurrence_pattern("every day")
        assert result["type"] == RecurrenceType.DAILY
        assert result["interval"] == 1
        
        # Test weekly patterns
        result = service.parse_recurrence_pattern("weekly")
        assert result["type"] == RecurrenceType.WEEKLY
        assert result["interval"] == 1
        
        # Test monthly patterns
        result = service.parse_recurrence_pattern("monthly")
        assert result["type"] == RecurrenceType.MONTHLY
        assert result["interval"] == 1
        
        # Test yearly patterns
        result = service.parse_recurrence_pattern("yearly")
        assert result["type"] == RecurrenceType.YEARLY
        assert result["interval"] == 1
    
    def test_parse_interval_patterns(self):
        """Test parsing of interval-based recurrence patterns."""
        service = RecurringTaskService(None)
        
        # Test "every N days"
        result = service.parse_recurrence_pattern("every 3 days")
        assert result["type"] == RecurrenceType.DAILY
        assert result["interval"] == 3
        
        # Test "every N weeks"
        result = service.parse_recurrence_pattern("every 2 weeks")
        assert result["type"] == RecurrenceType.WEEKLY
        assert result["interval"] == 2
        
        # Test "every N months"
        result = service.parse_recurrence_pattern("every 6 months")
        assert result["type"] == RecurrenceType.MONTHLY
        assert result["interval"] == 6
        
        # Test "every N years"
        result = service.parse_recurrence_pattern("every 2 years")
        assert result["type"] == RecurrenceType.YEARLY
        assert result["interval"] == 2
    
    def test_parse_weekday_patterns(self):
        """Test parsing of weekday-based recurrence patterns."""
        service = RecurringTaskService(None)
        
        # Test weekdays
        result = service.parse_recurrence_pattern("weekdays")
        assert result["type"] == RecurrenceType.CUSTOM
        assert result["weekdays"] == [0, 1, 2, 3, 4]  # Mon-Fri
        
        # Test weekends
        result = service.parse_recurrence_pattern("weekends")
        assert result["type"] == RecurrenceType.CUSTOM
        assert result["weekdays"] == [5, 6]  # Sat-Sun
        
        # Test specific weekdays
        result = service.parse_recurrence_pattern("every monday,wednesday,friday")
        assert result["type"] == RecurrenceType.CUSTOM
        assert result["weekdays"] == [0, 2, 4]  # Mon, Wed, Fri
    
    def test_parse_invalid_patterns(self):
        """Test parsing of invalid recurrence patterns."""
        service = RecurringTaskService(None)
        
        # Test empty pattern
        with pytest.raises(ValueError):
            service.parse_recurrence_pattern("")
        
        # Test invalid pattern
        with pytest.raises(ValueError):
            service.parse_recurrence_pattern("invalid pattern")
    
    def test_generate_daily_recurring_dates(self):
        """Test generation of daily recurring dates."""
        service = RecurringTaskService(None)
        
        start_date = datetime(2025, 1, 1, 10, 0, 0)
        recurrence_data = {"type": RecurrenceType.DAILY, "interval": 1}
        
        dates = service.generate_recurring_dates(
            start_date=start_date,
            recurrence_data=recurrence_data,
            count=5
        )
        
        assert len(dates) == 5
        assert dates[0] == start_date
        assert dates[1] == start_date + timedelta(days=1)
        assert dates[2] == start_date + timedelta(days=2)
        assert dates[3] == start_date + timedelta(days=3)
        assert dates[4] == start_date + timedelta(days=4)
    
    def test_generate_weekly_recurring_dates(self):
        """Test generation of weekly recurring dates."""
        service = RecurringTaskService(None)
        
        start_date = datetime(2025, 1, 1, 10, 0, 0)  # Wednesday
        recurrence_data = {"type": RecurrenceType.WEEKLY, "interval": 1}
        
        dates = service.generate_recurring_dates(
            start_date=start_date,
            recurrence_data=recurrence_data,
            count=3
        )
        
        assert len(dates) == 3
        assert dates[0] == start_date
        assert dates[1] == start_date + timedelta(weeks=1)
        assert dates[2] == start_date + timedelta(weeks=2)
    
    def test_generate_monthly_recurring_dates(self):
        """Test generation of monthly recurring dates."""
        service = RecurringTaskService(None)
        
        start_date = datetime(2025, 1, 15, 10, 0, 0)
        recurrence_data = {"type": RecurrenceType.MONTHLY, "interval": 1}
        
        dates = service.generate_recurring_dates(
            start_date=start_date,
            recurrence_data=recurrence_data,
            count=3
        )
        
        assert len(dates) == 3
        assert dates[0] == start_date
        assert dates[1] == datetime(2025, 2, 15, 10, 0, 0)
        assert dates[2] == datetime(2025, 3, 15, 10, 0, 0)
    
    def test_generate_weekday_recurring_dates(self):
        """Test generation of weekday-based recurring dates."""
        service = RecurringTaskService(None)
        
        # Start on a Monday (2025-01-06)
        start_date = datetime(2025, 1, 6, 10, 0, 0)
        recurrence_data = {"type": RecurrenceType.CUSTOM, "weekdays": [0, 2, 4]}  # Mon, Wed, Fri
        
        dates = service.generate_recurring_dates(
            start_date=start_date,
            recurrence_data=recurrence_data,
            count=5
        )
        
        assert len(dates) == 5
        # Should be Mon, Wed, Fri, Mon, Wed
        expected_dates = [
            datetime(2025, 1, 6, 10, 0, 0),   # Monday
            datetime(2025, 1, 8, 10, 0, 0),   # Wednesday
            datetime(2025, 1, 10, 10, 0, 0),  # Friday
            datetime(2025, 1, 13, 10, 0, 0),  # Monday
            datetime(2025, 1, 15, 10, 0, 0),  # Wednesday
        ]
        
        for i, expected_date in enumerate(expected_dates):
            assert dates[i].date() == expected_date.date()
    
    def test_generate_with_end_date(self):
        """Test generation of recurring dates with end date limit."""
        service = RecurringTaskService(None)
        
        start_date = datetime(2025, 1, 1, 10, 0, 0)
        end_date = datetime(2025, 1, 5, 10, 0, 0)
        recurrence_data = {"type": RecurrenceType.DAILY, "interval": 1}
        
        dates = service.generate_recurring_dates(
            start_date=start_date,
            recurrence_data=recurrence_data,
            end_date=end_date
        )
        
        # Should generate dates for Jan 1, 2, 3, 4 (end_date is exclusive)
        assert len(dates) == 4
        assert all(date < end_date for date in dates)
    
    def test_generate_with_count_limit(self):
        """Test generation of recurring dates with count limit."""
        service = RecurringTaskService(None)
        
        start_date = datetime(2025, 1, 1, 10, 0, 0)
        recurrence_data = {"type": RecurrenceType.DAILY, "interval": 1}
        
        dates = service.generate_recurring_dates(
            start_date=start_date,
            recurrence_data=recurrence_data,
            count=3
        )
        
        assert len(dates) == 3
    
    def test_date_matches_pattern_weekdays(self):
        """Test date matching for weekday patterns."""
        service = RecurringTaskService(None)
        
        # Monday
        monday = datetime(2025, 1, 6, 10, 0, 0)
        # Saturday
        saturday = datetime(2025, 1, 11, 10, 0, 0)
        
        weekdays_pattern = {"type": RecurrenceType.CUSTOM, "weekdays": [0, 1, 2, 3, 4]}
        
        assert service._date_matches_pattern(monday, weekdays_pattern) is True
        assert service._date_matches_pattern(saturday, weekdays_pattern) is False
    
    def test_get_next_date_daily(self):
        """Test getting next date for daily recurrence."""
        service = RecurringTaskService(None)
        
        current_date = datetime(2025, 1, 1, 10, 0, 0)
        recurrence_data = {"type": RecurrenceType.DAILY, "interval": 2}
        
        next_date = service._get_next_date(current_date, RecurrenceType.DAILY, recurrence_data)
        
        assert next_date == current_date + timedelta(days=2)
    
    def test_get_next_date_monthly_edge_case(self):
        """Test getting next date for monthly recurrence with edge cases."""
        service = RecurringTaskService(None)
        
        # Test January 31 -> February (should become Feb 28/29)
        jan_31 = datetime(2025, 1, 31, 10, 0, 0)
        recurrence_data = {"type": RecurrenceType.MONTHLY, "interval": 1}
        
        next_date = service._get_next_date(jan_31, RecurrenceType.MONTHLY, recurrence_data)
        
        # Should be February 28, 2025 (not a leap year)
        assert next_date == datetime(2025, 2, 28, 10, 0, 0)
    
    def test_get_next_date_yearly_leap_year(self):
        """Test getting next date for yearly recurrence with leap year edge case."""
        service = RecurringTaskService(None)
        
        # Test Feb 29 on a leap year -> next year (should become Feb 28)
        feb_29 = datetime(2024, 2, 29, 10, 0, 0)  # 2024 is a leap year
        recurrence_data = {"type": RecurrenceType.YEARLY, "interval": 1}
        
        next_date = service._get_next_date(feb_29, RecurrenceType.YEARLY, recurrence_data)
        
        # Should be February 28, 2025 (not a leap year)
        assert next_date == datetime(2025, 2, 28, 10, 0, 0)
