from app.core.db.base_model import BaseModel

from app.auth.models.token import Token
from app.auth.models.user import User
from app.auth.models.email_verification import EmailVerification
from app.auth.models.password_reset import PasswordReset
from app.auth.models.friends import Friendship
from app.auth.models.gear import Gear
from app.auth.models.user_gear import UserGear
from app.auth.models.achievements import Achievement
from app.auth.models.comments import Comment
from app.auth.models.news import News