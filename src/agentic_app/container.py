"""Application-level dependency injection container.

Uses ``dependency-injector`` to wire the full dependency graph::

    .env  -->  Pydantic Settings  -->  Dataclass Configs
          -->  Async API Clients (Resource lifecycle)
          -->  Application Services

Usage::

    container = Container()
    await container.init_resources()

    svc = container.accounting_service()
    funds = await svc.get_all_funds()

    await container.shutdown_resources()
"""

from __future__ import annotations

from dependency_injector import (
    containers,
    providers,
)

from .application.services.accounting_service import AccountingService
from .infrastructure.business_central_api import (
    BusinessCentralConfig,
    create_client as create_bc_client,
)
from .infrastructure.configs import (
    BusinessCentralODataApiSettings,
    FundAccountingApiSettings,
)
from .infrastructure.fund_accounting_api import (
    FundAccountingConfig,
    create_client as create_fa_client,
)


class Container(containers.DeclarativeContainer):
    """Application-level DI container.

    Layers:
        1. **Settings** -- Pydantic ``BaseSettings`` singletons (loaded from ``.env``).
        2. **Configs** -- Frozen dataclass singletons derived from settings.
        3. **Clients** -- Async ``Resource`` providers (lifecycle-managed).
        4. **Services** -- Application services wired to clients.
    """

    # -----------------------------------------------------------------
    # Layer 1: Settings (load from .env once)
    # -----------------------------------------------------------------

    bc_settings = providers.Singleton(BusinessCentralODataApiSettings)
    fa_settings = providers.Singleton(FundAccountingApiSettings)

    # -----------------------------------------------------------------
    # Layer 2: Infrastructure configs (derived from settings)
    # -----------------------------------------------------------------

    bc_config = providers.Singleton(
        BusinessCentralConfig,
        base_url=bc_settings.provided.odata_base_url,
        tenant=bc_settings.provided.odata_tenant,
        username=bc_settings.provided.odata_username,
        password=bc_settings.provided.odata_password,
    )

    fa_config = providers.Singleton(
        FundAccountingConfig,
        base_url=fa_settings.provided.base_url,
        tenant_name=fa_settings.provided.tenant_name, 
        company_name=fa_settings.provided.company_name, 
        client_id=fa_settings.provided.client_id, 
        client_secret=fa_settings.provided.client_secret,
    )

    # -----------------------------------------------------------------
    # Layer 3: Async clients (Resource manages init/shutdown)
    # -----------------------------------------------------------------

    bc_client = providers.Resource(
        create_bc_client,
        config=bc_config,
    )

    fa_client = providers.Resource(
        create_fa_client,
        config=fa_config,
    )

    # -----------------------------------------------------------------
    # Layer 4: Application services
    # -----------------------------------------------------------------

    accounting_service = providers.Factory(
        AccountingService,
        business_central_client=bc_client,
    )
