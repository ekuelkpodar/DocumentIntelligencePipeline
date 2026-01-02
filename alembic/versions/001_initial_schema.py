"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-01-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgvector"')

    # Create enums
    document_type_enum = postgresql.ENUM(
        'invoice', 'receipt', 'menu', 'form', 'contract', 'unknown',
        name='document_type',
        create_type=True
    )
    document_type_enum.create(op.get_bind())

    processing_status_enum = postgresql.ENUM(
        'pending', 'processing', 'extracting', 'validating',
        'completed', 'failed', 'needs_review',
        name='processing_status',
        create_type=True
    )
    processing_status_enum.create(op.get_bind())

    confidence_level_enum = postgresql.ENUM(
        'high', 'medium', 'low', 'very_low',
        name='confidence_level',
        create_type=True
    )
    confidence_level_enum.create(op.get_bind())

    # Documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('original_filename', sa.String(500), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger, nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('document_type', document_type_enum, server_default='unknown'),
        sa.Column('document_type_confidence', sa.Float, nullable=True),
        sa.Column('page_count', sa.Integer, server_default='1'),
        sa.Column('status', processing_status_enum, server_default='pending'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_duration_ms', sa.Integer, nullable=True),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('tokens_used', sa.Integer, nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
        sa.Column('created_by', sa.String(255), nullable=True),
    )

    op.create_index('idx_documents_status', 'documents', ['status'])
    op.create_index('idx_documents_type', 'documents', ['document_type'])
    op.create_index('idx_documents_created', 'documents', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_documents_external_id', 'documents', ['external_id'])
    op.create_index('idx_documents_hash', 'documents', ['file_hash'])

    # Extractions table
    op.create_table(
        'extractions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_number', sa.Integer, server_default='1'),
        sa.Column('raw_response', postgresql.JSONB, nullable=False),
        sa.Column('structured_data', postgresql.JSONB, nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('confidence_level', confidence_level_enum, nullable=True),
        sa.Column('extraction_model', sa.String(100), nullable=True),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('tokens_input', sa.Integer, nullable=True),
        sa.Column('tokens_output', sa.Integer, nullable=True),
        sa.Column('is_validated', sa.Boolean, server_default='false'),
        sa.Column('validated_by', sa.String(255), nullable=True),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validation_corrections', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('document_id', 'page_number', name='unique_doc_page'),
    )

    op.create_index('idx_extractions_document', 'extractions', ['document_id'])
    op.create_index('idx_extractions_confidence', 'extractions', ['confidence_score'])

    # Invoices table
    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('extraction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('extractions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('invoice_date', sa.Date, nullable=True),
        sa.Column('due_date', sa.Date, nullable=True),
        sa.Column('purchase_order_number', sa.String(100), nullable=True),
        sa.Column('vendor_name', sa.String(500), nullable=True),
        sa.Column('vendor_address', sa.Text, nullable=True),
        sa.Column('vendor_tax_id', sa.String(50), nullable=True),
        sa.Column('vendor_email', sa.String(255), nullable=True),
        sa.Column('vendor_phone', sa.String(50), nullable=True),
        sa.Column('customer_name', sa.String(500), nullable=True),
        sa.Column('customer_address', sa.Text, nullable=True),
        sa.Column('customer_account_number', sa.String(100), nullable=True),
        sa.Column('subtotal', sa.Numeric(15, 2), nullable=True),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('discount_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('shipping_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('payment_terms', sa.String(100), nullable=True),
        sa.Column('payment_method', sa.String(100), nullable=True),
        sa.Column('bank_account', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    op.create_index('idx_invoices_vendor_trgm', 'invoices', ['vendor_name'], postgresql_using='gin', postgresql_ops={'vendor_name': 'gin_trgm_ops'})
    op.create_index('idx_invoices_date', 'invoices', ['invoice_date'])
    op.create_index('idx_invoices_total', 'invoices', ['total_amount'])

    # Invoice line items
    op.create_table(
        'invoice_line_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('line_number', sa.Integer, nullable=True),
        sa.Column('item_code', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('quantity', sa.Numeric(15, 4), nullable=True),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('unit_price', sa.Numeric(15, 4), nullable=True),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('tax_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('line_total', sa.Numeric(15, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    op.create_index('idx_line_items_invoice', 'invoice_line_items', ['invoice_id'])
    op.create_index('idx_line_items_description', 'invoice_line_items', ['description'], postgresql_using='gin', postgresql_ops={'description': 'gin_trgm_ops'})

    # Receipts table
    op.create_table(
        'receipts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('extraction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('extractions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('merchant_name', sa.String(500), nullable=True),
        sa.Column('merchant_address', sa.Text, nullable=True),
        sa.Column('merchant_phone', sa.String(50), nullable=True),
        sa.Column('receipt_number', sa.String(100), nullable=True),
        sa.Column('transaction_date', sa.Date, nullable=True),
        sa.Column('transaction_time', sa.Time, nullable=True),
        sa.Column('subtotal', sa.Numeric(15, 2), nullable=True),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('tip_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('payment_method', sa.String(100), nullable=True),
        sa.Column('card_last_four', sa.String(4), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    op.create_index('idx_receipts_merchant_trgm', 'receipts', ['merchant_name'], postgresql_using='gin', postgresql_ops={'merchant_name': 'gin_trgm_ops'})
    op.create_index('idx_receipts_date', 'receipts', ['transaction_date'])
    op.create_index('idx_receipts_category', 'receipts', ['category'])

    # Receipt line items
    op.create_table(
        'receipt_line_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('receipt_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('receipts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('quantity', sa.Numeric(10, 3), server_default='1'),
        sa.Column('unit_price', sa.Numeric(15, 2), nullable=True),
        sa.Column('line_total', sa.Numeric(15, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    op.create_index('idx_receipt_line_items_receipt', 'receipt_line_items', ['receipt_id'])

    # Menus table
    op.create_table(
        'menus',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('extraction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('extractions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('restaurant_name', sa.String(500), nullable=True),
        sa.Column('cuisine_type', sa.String(100), nullable=True),
        sa.Column('menu_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    # Menu items
    op.create_table(
        'menu_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('menu_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('menus.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(200), nullable=True),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('is_vegetarian', sa.Boolean, nullable=True),
        sa.Column('is_vegan', sa.Boolean, nullable=True),
        sa.Column('is_gluten_free', sa.Boolean, nullable=True),
        sa.Column('is_spicy', sa.Boolean, nullable=True),
        sa.Column('spice_level', sa.Integer, nullable=True),
        sa.Column('allergens', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('calories', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    op.create_index('idx_menu_items_menu', 'menu_items', ['menu_id'])
    op.create_index('idx_menu_items_name_trgm', 'menu_items', ['name'], postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
    op.create_index('idx_menu_items_category', 'menu_items', ['category'])

    # Extraction templates
    op.create_table(
        'extraction_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('document_type', document_type_enum, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('system_prompt', sa.Text, nullable=False),
        sa.Column('extraction_schema', postgresql.JSONB, nullable=False),
        sa.Column('validation_rules', postgresql.JSONB, nullable=True),
        sa.Column('examples', postgresql.JSONB, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('version', sa.Integer, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('created_by', sa.String(255), nullable=True),
    )

    # Webhook subscriptions
    op.create_table(
        'webhook_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('url', sa.String(2000), nullable=False),
        sa.Column('secret', sa.String(255), nullable=False),
        sa.Column('events', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('max_retries', sa.Integer, server_default='3'),
        sa.Column('retry_delay_seconds', sa.Integer, server_default='60'),
        sa.Column('total_delivered', sa.Integer, server_default='0'),
        sa.Column('total_failed', sa.Integer, server_default='0'),
        sa.Column('last_delivery_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure_reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('created_by', sa.String(255), nullable=True),
    )

    # Webhook deliveries
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('webhook_subscriptions.id'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('payload', postgresql.JSONB, nullable=False),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('attempts', sa.Integer, server_default='0'),
        sa.Column('response_status_code', sa.Integer, nullable=True),
        sa.Column('response_body', sa.Text, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Audit log
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('actor', sa.String(255), nullable=True),
        sa.Column('old_values', postgresql.JSONB, nullable=True),
        sa.Column('new_values', postgresql.JSONB, nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    op.create_index('idx_audit_entity', 'audit_log', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_created', 'audit_log', ['created_at'], postgresql_ops={'created_at': 'DESC'})


def downgrade() -> None:
    """Drop all tables and enums."""
    op.drop_table('audit_log')
    op.drop_table('webhook_deliveries')
    op.drop_table('webhook_subscriptions')
    op.drop_table('extraction_templates')
    op.drop_table('menu_items')
    op.drop_table('menus')
    op.drop_table('receipt_line_items')
    op.drop_table('receipts')
    op.drop_table('invoice_line_items')
    op.drop_table('invoices')
    op.drop_table('extractions')
    op.drop_table('documents')

    op.execute('DROP TYPE IF EXISTS confidence_level')
    op.execute('DROP TYPE IF EXISTS processing_status')
    op.execute('DROP TYPE IF EXISTS document_type')
    op.execute('DROP EXTENSION IF EXISTS pgvector')
    op.execute('DROP EXTENSION IF EXISTS pg_trgm')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
