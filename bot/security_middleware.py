import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext

from bot.security_manager import security_manager
from bot.config import config

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseMiddleware):
    """Security middleware for aiogram bot."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process event through security checks."""
        
        # Extract user ID
        user_id = self._extract_user_id(event)
        if not user_id:
            logger.warning("🚫 Event rejected: Could not extract user ID")
            return
        
        # Check rate limiting
        action = self._get_action_name(event)
        if not await security_manager.check_rate_limit(user_id, action):
            await self._handle_rate_limit_exceeded(event, user_id, action)
            return
        
        # Validate input data for web app messages
        if isinstance(event, Message) and event.web_app_data:
            validation_result = await self._validate_web_app_data(event.web_app_data.data)
            if not validation_result[0]:
                logger.warning(f"🚫 Web app data validation failed for user {user_id}: {validation_result[1]}")
                await self._handle_validation_failure(event, user_id, validation_result[1])
                return
        
        # Log security event
        security_manager._log_security_event("bot_interaction", {
            "user_id": user_id,
            "action": action,
            "event_type": type(event).__name__
        })
        
        # Continue with handler
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"🚨 Error in bot handler for user {user_id}: {e}")
            security_manager._log_security_event("handler_error", {
                "user_id": user_id,
                "action": action,
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def _extract_user_id(self, event: TelegramObject) -> int:
        """Extract user ID from different event types."""
        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None
        return None
    
    def _get_action_name(self, event: TelegramObject) -> str:
        """Get action name for rate limiting."""
        if isinstance(event, Message):
            if event.web_app_data:
                return "web_app_data"
            elif event.text:
                return f"text_{event.text}"
            elif event.photo:
                return "photo"
            elif event.document:
                return "document"
            else:
                return "message"
        elif isinstance(event, CallbackQuery):
            return f"callback_{event.data}"
        return "unknown"
    
    async def _validate_web_app_data(self, data_str: str) -> tuple[bool, list[str]]:
        """Validate web app data structure."""
        try:
            import json
            data = json.loads(data_str)
            
            # Define expected structure for different actions
            if "action" in data:
                action = data["action"]
                
                if action == "update_cart":
                    expected_structure = {
                        "action": "str",
                        "product_id": "str",
                        "quantity": "int"
                    }
                elif action == "checkout_order":
                    expected_structure = {
                        "action": "str",
                        "order_details": "dict",
                        "cart_items": "list",
                        "total_amount": "float"
                    }
                else:
                    expected_structure = {"action": "str"}
                
                return security_manager.validate_input_data(data, expected_structure)
            else:
                return False, ["Missing action field"]
                
        except json.JSONDecodeError:
            return False, ["Invalid JSON format"]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    async def _handle_rate_limit_exceeded(self, event: TelegramObject, user_id: int, action: str):
        """Handle rate limit exceeded."""
        if isinstance(event, Message):
            await event.answer(
                "⚠️ Слишком много запросов. Пожалуйста, подождите немного перед следующим действием.",
                reply_markup=None
            )
        elif isinstance(event, CallbackQuery):
            await event.answer(
                "⚠️ Слишком много запросов. Пожалуйста, подождите немного.",
                show_alert=True
            )
    
    async def _handle_validation_failure(self, event: TelegramObject, user_id: int, errors: list[str]):
        """Handle validation failure."""
        error_message = "❌ Ошибка валидации данных:\n" + "\n".join(f"• {error}" for error in errors)
        
        if isinstance(event, Message):
            await event.answer(
                error_message,
                reply_markup=None
            )

class FSMContextMiddleware(BaseMiddleware):
    """Middleware for FSM context security."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process FSM context through security checks."""
        
        # Get FSM context
        fsm_context: FSMContext = data.get("fsm_context")
        if fsm_context:
            # Validate FSM state
            current_state = await fsm_context.get_state()
            if current_state:
                # Log FSM state changes
                user_id = self._extract_user_id(event)
                if user_id:
                    security_manager._log_security_event("fsm_state_change", {
                        "user_id": user_id,
                        "state": current_state,
                        "event_type": type(event).__name__
                    })
        
        return await handler(event, data)
    
    def _extract_user_id(self, event: TelegramObject) -> int:
        """Extract user ID from event."""
        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None
        return None

# Create middleware instances
security_middleware = SecurityMiddleware()
fsm_context_middleware = FSMContextMiddleware()
