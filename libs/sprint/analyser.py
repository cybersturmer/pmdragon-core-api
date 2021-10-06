from collections import namedtuple
from datetime import timedelta, date, datetime

from django.db.models import Sum

from apps.core.models import ProjectWorkingDays, Sprint, SprintEffortsHistory

MarkedElement = namedtuple('MarkedElement', [
	'time',
	'is_working',
	'story_points'
])


class SprintAnalyser:
	"""
	We use this class to build
	estimation and actual efforts chart for
	BurnDown Chart.
	What information do we need to build estimation efforts chart:
	1) How many working days do we have?
		a) Standard working days
		b) Non-working days
		c) Sprint start
		d) Sprint end
	2) How many Story Points do we have?
	Result => ((datetime, SP), (datetime, SP))
	What information do we need to build actual efforts chart:
	1) History of completion:
		a) Day
		b) Completed Story Points
	"""

	def __init__(self,
				 sprint: Sprint,
				 working_days: ProjectWorkingDays):

		self.sprint = sprint
		self.working_days = working_days

	def get_total_story_points_of_first_entry_of_sprint_efforts_history(self) -> int:
		"""
		When we create a Sprint - we calculate entry with total story points
		and completed story points (usually 0).
		Sprint scope can be changed after sprint is started.
		So we use history to remember total story points when sprint just started.
		Here we can get this historical first total story points """
		history_entry = SprintEffortsHistory \
			.objects \
			.filter(
				workspace=self.sprint.workspace,
				project=self.sprint.project,
				sprint=self.sprint
			) \
			.order_by('point_at') \
			.first()

		return history_entry.total_value

	def calculate_total_story_points(self) -> int:
		"""
		We use this method to get the total amount of story points
		for the current Sprint.
		@return: Just number like 48
		"""
		aggregation = self.sprint \
			.issues \
			.filter(estimation_category__isnull=False) \
			.aggregate(total=Sum('estimation_category__value'))

		return aggregation['total']

	def calculate_completed_story_points(self) -> int:
		"""
		We use this to get the total amount of story points
		for issues in the current Sprint that were set to the "is_done" state.
		@return: Just number like 48
		"""
		aggregation = self.sprint\
			.issues \
			.filter(estimation_category__isnull=False,
					state_category__is_done=True) \
			.aggregate(total=Sum('estimation_category__value'))

		return aggregation['total'] if aggregation['total'] is not None else 0

	def calculate_not_completed_story_points(self) -> int:
		"""
		We use this to get the total amount od story points
		for issues in the current Sprint that were not in the "is_done" state
		@return: Just number like 48
		"""
		aggregation = self.sprint \
			.issues \
			.filter(estimation_category__isnull=False,
					state_category__is_done=False) \
			.aggregate(total=Sum('estimation_category__value'))

		return aggregation['total']

	def calculate_day_series(self) -> tuple:
		"""
		This method helps us to calculate day points for sprint
		@return: for example:
		- datetime for Sprint started_at, like 02 October 2021 4PM
		- datetime (one day later), like 03 October 2021 4PM
		- (one day later) .....
		- datetime for Sprint finished_at, like 16 October 2021 6PM
		"""
		days_series = []

		for day in range(self.sprint.days + 1):
			one_day_later = self.sprint.started_at + timedelta(days=day)

			next_series_element = one_day_later \
				if one_day_later < self.sprint.finished_at \
				else self.sprint.finished_at

			days_series.append(next_series_element)

		return tuple(days_series)

	def is_working_day_for_project(self, day: date) -> bool:
		"""
		We use this method to understand is this working day or non-working
		@param day: datetime.day
		@return: Just Boolean (True or False)
		"""
		weekday_decision_tree = {
			0: self.working_days.monday,
			1: self.working_days.tuesday,
			2: self.working_days.wednesday,
			3: self.working_days.thursday,
			4: self.working_days.friday,
			5: self.working_days.saturday,
			6: self.working_days.sunday
		}

		is_not_in_non_working_day = day not in self.working_days.non_working_days.all()
		is_standard_working_day = weekday_decision_tree[day.weekday()]

		return is_standard_working_day and is_not_in_non_working_day

	def calculate_marked_is_working_series(self) -> tuple:
		"""
		We use this method to generate tuple with:
		1) datetime
		2) Boolean (True / False) is this day a working day
		3) Story points amount (by default zero)
		@return:
		"""
		marked_series = []
		days_series = self.calculate_day_series()

		for day in days_series:
			marked_series.append(
				{
					'time': day,
					'is_working': self.is_working_day_for_project(day.date()),
					'story_points': 0
				}
			)

		return tuple(marked_series)

	def calculate_estimated_efforts_distribution(self):
		total_story_points = self.get_total_story_points_of_first_entry_of_sprint_efforts_history()

		marked_day_series = self.calculate_marked_is_working_series()
		working_marked_day_series: list[dict] = [element
												 for element
												 in marked_day_series
												 if element['is_working']]

		working_marked_day_series_length = len(working_marked_day_series)

		# @todo Please check if that approach works for theoretical and crazy 1 day long Sprint.
		normal_story_points_distribution = total_story_points / (working_marked_day_series_length - 1) \
			if working_marked_day_series_length \
			else total_story_points

		_estimation = total_story_points
		for index, element in enumerate(marked_day_series):
			previous_day_is_working = index > 0 and marked_day_series[index - 1]['is_working']
			_decrement = normal_story_points_distribution if previous_day_is_working else 0
			_estimation -= _decrement

			element['story_points'] = round(_estimation)

		return marked_day_series
