from contextlib import AbstractAsyncContextManager
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    Literal,
    Mapping,
    Optional,
    Sequence,
    TypeVar,
    List,
    Union,
)

from apmodel import Activity
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.params import Depends
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.routing import BaseRoute

from apkit.server.routes.outbox import create_outbox_route

from ..abc.server import AbstractApkitIntegration
from ..client.models import Resource as WebfingerResource
from ..types import Outbox
from .subrouter import SubRouter
from .types import ActorKey, Context

from ..config import AppConfig
from .routes.nodeinfo import nodeinfo_links_route
from .routes.inbox import create_inbox_route

AppType = TypeVar("AppType", bound="ActivityPubServer")


class ActivityPubServer(AbstractApkitIntegration, FastAPI):
    def __init__(
        self: AppType,
        *,
        apkit_config: AppConfig = AppConfig(),
        debug: bool = False,
        routes: List[BaseRoute] | None = None,
        title: str = "FastAPI",
        summary: str | None = None,
        description: str = "",
        version: str = "0.1.0",
        openapi_url: str | None = "/openapi.json",
        openapi_tags: List[Dict[str, Any]] | None = None,
        servers: List[Dict[str, str | Any]] | None = None,
        dependencies: Optional[Sequence[Depends]] = None,
        default_response_class: type[Response] = JSONResponse,
        redirect_slashes: bool = True,
        docs_url: str | None = "/docs",
        redoc_url: str | None = "/redoc",
        swagger_ui_oauth2_redirect_url: str | None = "/docs/oauth2-redirect",
        swagger_ui_init_oauth: Dict[str, Any] | None = None,
        middleware: Sequence[Middleware] | None = None,
        exception_handlers: Dict[
            int | type[Exception],
            Callable[[Request, Any], Coroutine[Any, Any, Response]],
        ]
        | None = None,
        on_startup: Sequence[Callable[[], Any]] | None = None,
        on_shutdown: Sequence[Callable[[], Any]] | None = None,
        lifespan: Callable[[AppType], AbstractAsyncContextManager[None, bool | None]]
        | Callable[
            [AppType], AbstractAsyncContextManager[Mapping[str, Any], bool | None]
        ]
        | None = None,
        terms_of_service: str | None = None,
        contact: Dict[str, str | Any] | None = None,
        license_info: Dict[str, str | Any] | None = None,
        openapi_prefix: str = "",
        root_path: str = "",
        root_path_in_servers: bool = True,
        responses: Dict[int | str, Dict[str, Any]] | None = None,
        callbacks: List[BaseRoute] | None = None,
        webhooks: APIRouter | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        swagger_ui_parameters: Dict[str, Any] | None = None,
        generate_unique_id_function: Callable[[APIRoute], str] = generate_unique_id,
        separate_input_output_schemas: bool = True,
        **extra: Any,
    ) -> None:
        self.__ap_events = {}
        self.__ap_outbox: Optional[Callable[[Context], Awaitable[Any]]] = None
        self.__ap_webfinger_route: Optional[Callable[[Request,WebfingerResource], Awaitable[Any]]] = None
        self.__ap_config = apkit_config
        self._get_actor_keys: Optional[Callable[[str], Awaitable[List["ActorKey"]]]] = (
            apkit_config.actor_keys
        )
        self.__ap_config = apkit_config

        super().__init__(
            debug=debug,
            routes=routes,
            title=title,
            summary=summary,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=openapi_tags,
            servers=servers,
            dependencies=dependencies,
            default_response_class=default_response_class,
            redirect_slashes=redirect_slashes,
            docs_url=docs_url,
            redoc_url=redoc_url,
            swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
            swagger_ui_init_oauth=swagger_ui_init_oauth,
            middleware=middleware,
            exception_handlers=exception_handlers,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            terms_of_service=terms_of_service,
            contact=contact,
            license_info=license_info,
            openapi_prefix=openapi_prefix,
            root_path=root_path,
            root_path_in_servers=root_path_in_servers,
            responses=responses,
            callbacks=callbacks,
            webhooks=webhooks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            swagger_ui_parameters=swagger_ui_parameters,
            generate_unique_id_function=generate_unique_id_function,
            separate_input_output_schemas=separate_input_output_schemas,
            **extra,
        )

    async def __inbox_route(self, request: Request):
        r = create_inbox_route(
            apkit=self, config=self.__ap_config, routes=self.__ap_events
        )
        return await r(request=request)

    async def __outbox_route(self, request: Request):
        if self.__ap_outbox:
            r = create_outbox_route(self, self.__ap_outbox)
            if r:
                return await r(request=request)
        return Response("Not Found", status_code=404)

    async def __webfinger_route(self, request: Request):
        func = self.__ap_webfinger_route
        if func:
            resource = request.query_params.get("resource")
            if resource:
                acct = WebfingerResource.parse(resource)
                return await func(request,acct)
        
    def setup(self) -> None:
        self.add_api_route(
            path="/.well-known/nodeinfo",
            endpoint=nodeinfo_links_route,
            methods=["GET"],
            name="__apkit_wellknown_nodeinfo",
        )
        self.add_api_route(
            path="/.well-known/webfinger",
            endpoint=self.__webfinger_route,
            methods=["GET"],
            name="__ap_webfinger",
            include_in_schema=False,
        )
        return super().setup()

    def on(self, type: Union[type[Activity], type[Outbox]], func: Optional[Callable] = None):
        def decorator(func: Callable) -> Callable:
            if  issubclass(type, Activity):
                self.__ap_events[type] = func
            elif issubclass(type, Outbox):
                self.__ap_outbox = func
            return func
        
        if func is not None:
            return decorator(func)

        return decorator

    def webfinger(self, func: Optional[Callable] = None):
        def decorator(func: Callable) -> Callable:
            self.__ap_webfinger_route = func
            return func
        
        if func is not None:
            return decorator(func)

        return decorator
        
    def outbox(self, *args) -> None:
        for path in args:
            self.add_api_route(
                path=path,
                endpoint=self.__outbox_route,
                methods=["GET"],
                name=f"__apkit_outbox_{path}",
                include_in_schema=False,
            )

    def inbox(self, *args) -> None:
        for path in args:
            self.add_api_route(
                path=path,
                endpoint=self.__inbox_route,
                methods=["POST"],
                name=f"__apkit_inbox_{path}",
                include_in_schema=False,
            )

    def nodeinfo(
        self,
        route: str,
        version: Literal["2.0", "2.1"],
        func: Optional[Callable] = None,
    ) -> Callable:
        """Define Nodeinfo route.

        Args:
            route (str): route path.
            version (Literal[&quot;2.0&quot;, &quot;2.1&quot;]): nodeinfo version
            func (Optional[FunctionType], optional): If use that as decorator, ignore this. Defaults to None.

        Returns:
            Union[None, Callable]: no description
        """

        def decorator(fn: Callable) -> Callable:
            if version == "2.0":
                self.add_api_route(
                    path=route,
                    endpoint=fn,
                    methods=["GET"],
                    name="__apkit_nodeinfo_2.0",
                    include_in_schema=False,
                )
            elif version == "2.1":
                self.add_api_route(
                    path=route,
                    endpoint=fn,
                    methods=["GET"],
                    name="__apkit_nodeinfo_2.1",
                    include_in_schema=False,
                )
            return fn

        if func is not None:
            return decorator(func)

        return decorator

    def include_router(
        self,
        router: APIRouter | SubRouter,
        *,
        prefix: str = "",
        tags: List[str | Enum] | None = None,
        dependencies: Sequence[Depends] | None = None,
        responses: Dict[int | str, Dict[str, Any]] | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        default_response_class: type[Response] = JSONResponse,
        callbacks: List[BaseRoute] | None = None,
        generate_unique_id_function: Callable[[APIRoute], str] = generate_unique_id,
    ) -> None:
        super().include_router(
            router,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            default_response_class=default_response_class,
            callbacks=callbacks,
            generate_unique_id_function=generate_unique_id_function,
        )
        if isinstance(router, SubRouter):
            self.__ap_events = {**router._ap_events, **self.__ap_events}
            self.__ap_outbox = self.__ap_outbox if not router._ap_outbox else router._ap_outbox
            self.__ap_webfinger_route = self.__ap_webfinger_route if not router._ap_webfinger_route else router._ap_webfinger_route
