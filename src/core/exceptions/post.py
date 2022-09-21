from core.exceptions.base import NotFoundException, ConflictException
from resources.strings import PostDoesNotFoundMessage, LikeAlreadyExistsMessage, LikeDoesNotExistsMessage


class PostDoesNotExists(NotFoundException):
    message = PostDoesNotFoundMessage


class LikeAlreadyExists(ConflictException):
    message = LikeAlreadyExistsMessage


class LikeDoesNotExists(NotFoundException):
    message = LikeDoesNotExistsMessage
