from src.domain.tasks import TaskRepository
from src.services.base import BaseUseCase


class TaskUseCase(BaseUseCase):
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo


from src.services.teams.get_member import GetMemberUseCase


class GetMemberDependantTaskUseCase(TaskUseCase):
    def __init__(
        self, task_repo: TaskRepository, get_member_use_case: GetMemberUseCase
    ):
        super().__init__(task_repo)
        self.get_member = get_member_use_case


from src.services.tasks.get_task import GetTaskUseCase


class GetTaskDependantTaskUseCase(TaskUseCase):
    def __init__(
        self,
        task_repo: TaskRepository,
        get_task_use_case: GetTaskUseCase,
    ):
        super().__init__(task_repo)
        self.get_task = get_task_use_case


class GetTaskMemberDependantTaskUseCase(GetTaskDependantTaskUseCase):
    def __init__(
        self,
        task_repo: TaskRepository,
        get_task_use_case: GetTaskUseCase,
        get_member_use_case: GetMemberUseCase,
    ):
        super().__init__(task_repo, get_task_use_case)
        self.get_member = get_member_use_case
