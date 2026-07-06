
from dishka import Provider, Scope, provide
from minio import Minio

from app.core.configs.app import app_config
from app.core.services.storage.aminio.policy import Policy
from app.core.services.storage.aminio.service import MinioStorageService
from app.core.services.storage.service import StorageService


class CoreProvider(Provider):

    @provide(scope=Scope.APP)
    def client_storage(self) -> Minio:
        return Minio(
            endpoint=app_config.storage_url,
            access_key=app_config.STORAGE_ACCESS_KEY,
            secret_key=app_config.STORAGE_SECRET_KEY,
            secure=app_config.ENVIRONMENT == "production",
        )

    @provide(scope=Scope.APP)
    def bucket_policy(self) -> dict[str, Policy]:
        return {
            "base": Policy.NONE
        }

    @provide(scope=Scope.APP)
    async def storage_service(self, client: Minio, bucket_policy: dict[str, Policy]) -> StorageService:
        return MinioStorageService(
            client=client,
            bucket_policy=bucket_policy
        )

