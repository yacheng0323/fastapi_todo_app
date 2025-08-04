"""Add user_id to todos and timestamps

Revision ID: 177da514fd36
Revises: c50296b27b45
Create Date: 2025-08-01 17:01:52.436028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '177da514fd36'
down_revision: Union[str, Sequence[str], None] = 'c50296b27b45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 🔧 方法 1：使用分步驟的方式添加欄位
    # 步驟 1：先添加基本欄位（沒有外鍵）
    with op.batch_alter_table("todo",schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id",sa.Integer(),nullable=True)) # 先設為 nullable
        batch_op.add_column(sa.Column("is_completed",sa.Boolean(),nullable=False,server_default="0"))

    # 步驟 2：再添加時間戳記欄位
    with op.batch_alter_table("todo",schema=None) as batch_op:
        batch_op.add_column(sa.Column("created_at",sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch_op.add_column(sa.Column("updated_at",sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))


    # 步驟 3：最後添加外鍵約束
    with op.batch_alter_table("todo",schema=None) as batch_op:
        batch_op.create_foreign_key("fk_todo_user_id", "user", ["user_id"], ["id"]) # 添加外鍵

   
def downgrade() -> None:
    """Downgrade schema."""
    # 反向操作：先移除外鍵，再移除欄位
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.drop_constraint('fk_todo_user_id', type_='foreignkey')
    
    # 移除 todo 表格的新增欄位
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('user_id')
        batch_op.drop_column('is_completed')
