from app.repository.geofence_violation_tracker_repository import \
    GeofenceViolationTrackerRepository
from app.service.base_service import BaseService


class GeofenceViolationTrackerService(BaseService):
    def __init__(
        self, geofence_violation_tracker_repository: GeofenceViolationTrackerRepository
    ):
        self.geofence_violation_tracker_repository = (
            geofence_violation_tracker_repository
        )
        super().__init__(geofence_violation_tracker_repository)
