/* eslint-disable */
/* tslint:disable */
// @ts-nocheck
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

/** Body_create_cost */
export interface BodyCreateCost {
  /**
   * Cost Name
   * @minLength 1
   * @maxLength 100
   */
  cost_name: string;
  /** Image */
  image: File | Blob;
  /** Video */
  video: File | Blob;
}

/** CostLikeChange */
export interface CostLikeChange {
  /** Is Liked */
  is_liked: 0 | 1;
}

/** CostLikeRead */
export interface CostLikeRead {
  /** Cost Id */
  cost_id: number;
  /** Is Liked */
  is_liked: 0 | 1;
  /** Like Count */
  like_count: number;
}

/** CostPublish */
export interface CostPublish {
  /**
   * Cost Description
   * @minLength 1
   * @maxLength 500
   */
  cost_description: string;
  /** Cost Behavior */
  cost_behavior: "fixed" | "variable";
  /**
   * Cost Code
   * @min 0
   */
  cost_code: number;
}

/** CostRead */
export interface CostRead {
  /** Cost Id */
  cost_id: number;
  /** Cost Name */
  cost_name: string;
  /** Cost Description */
  cost_description: string | null;
  /** Cost Status */
  cost_status: string;
  /** Cost Image Url */
  cost_image_url: string;
  /** Cost Video Url */
  cost_video_url: string;
  /** Cost Behavior */
  cost_behavior: string | null;
  /** Cost Code */
  cost_code: number | null;
  /**
   * Cost Created At
   * @format date-time
   */
  cost_created_at: string;
  /** Cost Creator Id */
  cost_creator_id: number;
  /** Cost Formed At */
  cost_formed_at: string | null;
  /** Like Count */
  like_count: number;
  /** Is Owner */
  is_owner: 0 | 1;
  /** Is Liked */
  is_liked: 0 | 1;
}

/** HTTPValidationError */
export interface HTTPValidationError {
  /** Detail */
  detail?: ValidationError[];
}

/** UserCredentials */
export interface UserCredentials {
  /**
   * User Name
   * @minLength 1
   * @maxLength 50
   */
  user_name: string;
  /**
   * Password
   * @minLength 1
   * @maxLength 128
   */
  password: string;
}

/** UserRead */
export interface UserRead {
  /** User Id */
  user_id: number;
  /** User Name */
  user_name: string;
}

/** UserRegister */
export interface UserRegister {
  /**
   * User Name
   * @minLength 1
   * @maxLength 50
   */
  user_name: string;
  /**
   * Password
   * @minLength 8
   * @maxLength 128
   */
  password: string;
}

/** ValidationError */
export interface ValidationError {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
  /** Input */
  input?: any;
  /** Context */
  ctx?: object;
}

export interface ListCostsParams {
  /** Min Cost Code */
  min_cost_code?: number | null;
  /** Max Cost Code */
  max_cost_code?: number | null;
}

export interface GetCostFeedParams {
  /** Cost Id */
  cost_id?: number | null;
  /**
   * Next
   * @default false
   */
  next?: boolean;
}

export interface PublishCostParams {
  /** Cost Id */
  costId: number;
}

export interface DeleteCostParams {
  /** Cost Id */
  costId: number;
}

export interface ChangeCostLikeParams {
  /** Cost Id */
  costId: number;
}

import type {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  HeadersDefaults,
  ResponseType,
} from "axios";
import axios from "axios";

export type QueryParamsType = Record<string | number, any>;

export interface FullRequestParams
  extends Omit<AxiosRequestConfig, "data" | "params" | "url" | "responseType"> {
  /** set parameter to `true` for call `securityWorker` for this request */
  secure?: boolean;
  /** request path */
  path: string;
  /** content type of request body */
  type?: ContentType;
  /** query params */
  query?: QueryParamsType;
  /** format of response (i.e. response.json() -> format: "json") */
  format?: ResponseType;
  /** request body */
  body?: unknown;
}

export type RequestParams = Omit<
  FullRequestParams,
  "body" | "method" | "query" | "path"
>;

export interface ApiConfig<SecurityDataType = unknown>
  extends Omit<AxiosRequestConfig, "data" | "cancelToken"> {
  securityWorker?: (
    securityData: SecurityDataType | null,
  ) => Promise<AxiosRequestConfig | void> | AxiosRequestConfig | void;
  secure?: boolean;
  format?: ResponseType;
}

export enum ContentType {
  Json = "application/json",
  JsonApi = "application/vnd.api+json",
  FormData = "multipart/form-data",
  UrlEncoded = "application/x-www-form-urlencoded",
  Text = "text/plain",
}

export class HttpClient<SecurityDataType = unknown> {
  public instance: AxiosInstance;
  private securityData: SecurityDataType | null = null;
  private securityWorker?: ApiConfig<SecurityDataType>["securityWorker"];
  private secure?: boolean;
  private format?: ResponseType;

  constructor({
    securityWorker,
    secure,
    format,
    ...axiosConfig
  }: ApiConfig<SecurityDataType> = {}) {
    this.instance = axios.create({
      ...axiosConfig,
      baseURL: axiosConfig.baseURL || "",
    });
    this.secure = secure;
    this.format = format;
    this.securityWorker = securityWorker;
  }

  public setSecurityData = (data: SecurityDataType | null) => {
    this.securityData = data;
  };

  protected mergeRequestParams(
    params1: AxiosRequestConfig,
    params2?: AxiosRequestConfig,
  ): AxiosRequestConfig {
    const method = params1.method || (params2 && params2.method);

    return {
      ...this.instance.defaults,
      ...params1,
      ...(params2 || {}),
      headers: {
        ...((method &&
          this.instance.defaults.headers[
            method.toLowerCase() as keyof HeadersDefaults
          ]) ||
          {}),
        ...(params1.headers || {}),
        ...((params2 && params2.headers) || {}),
      },
    };
  }

  protected stringifyFormItem(formItem: unknown) {
    if (typeof formItem === "object" && formItem !== null) {
      return JSON.stringify(formItem);
    } else {
      return `${formItem}`;
    }
  }

  protected createFormData(input: Record<string, unknown>): FormData {
    if (input instanceof FormData) {
      return input;
    }
    return Object.keys(input || {}).reduce((formData, key) => {
      const property = input[key];
      const propertyContent: any[] =
        property instanceof Array ? property : [property];

      for (const formItem of propertyContent) {
        const isFileType = formItem instanceof Blob || formItem instanceof File;
        formData.append(
          key,
          isFileType ? formItem : this.stringifyFormItem(formItem),
        );
      }

      return formData;
    }, new FormData());
  }

  public request = async <T = any, _E = any>({
    secure,
    path,
    type,
    query,
    format,
    body,
    ...params
  }: FullRequestParams): Promise<AxiosResponse<T>> => {
    const secureParams =
      ((typeof secure === "boolean" ? secure : this.secure) &&
        this.securityWorker &&
        (await this.securityWorker(this.securityData))) ||
      {};
    const requestParams = this.mergeRequestParams(params, secureParams);
    const responseFormat = format || this.format || undefined;

    if (
      type === ContentType.FormData &&
      body &&
      body !== null &&
      typeof body === "object"
    ) {
      body = this.createFormData(body as Record<string, unknown>);
    }

    if (
      type === ContentType.Text &&
      body &&
      body !== null &&
      typeof body !== "string"
    ) {
      body = JSON.stringify(body);
    }

    return this.instance.request({
      ...requestParams,
      headers: {
        ...(requestParams.headers || {}),
        ...(type ? { "Content-Type": type } : {}),
      },
      params: query,
      responseType: responseFormat,
      data: body,
      url: path,
    });
  };
}

/**
 * @title Масштаб — API издержек
 * @version 4.0.0
 *
 * ЛР4. Гость читает опубликованные издержки. После POST /api/users/auth браузер автоматически отправляет HttpOnly cookie cost_session. Создание, черновик, публикация, удаление и лайки требуют сессии Redis.
 */
export class Api<
  SecurityDataType extends unknown,
> extends HttpClient<SecurityDataType> {
  api = {
    /**
     * @description Доступен гостю. Только опубликованные карточки. min_cost_code и max_cost_code — включительный диапазон; is_owner — 0/1.
     *
     * @tags costs
     * @name ListCosts
     * @summary Список издержек с фильтром
     * @request GET:/api/costs
     */
    listCosts: (query: ListCostsParams = {}, params: RequestParams = {}) =>
      this.request<CostRead[], HTTPValidationError>({
        path: `/api/costs`,
        method: "GET",
        query: query,
        format: "json",
        ...params,
      }),

    /**
     * @description Три поля form-data: cost_name, image, video (файлы). Создатель, ID, статус draft и дата задаются сервером. Файлы сохраняются в MinIO.
     *
     * @tags costs
     * @name CreateCost
     * @summary Создать издержку с фото и видео
     * @request POST:/api/costs
     * @secure
     */
    createCost: (data: BodyCreateCost, params: RequestParams = {}) =>
      this.request<CostRead, void | HTTPValidationError>({
        path: `/api/costs`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.FormData,
        format: "json",
        ...params,
      }),

    /**
     * @description Доступен гостю. Без cost_id — первая карточка; cost_id и next=true — следующая по кругу. is_liked — 0/1 для текущего пользователя.
     *
     * @tags costs
     * @name GetCostFeed
     * @summary Одна карточка ленты
     * @request GET:/api/costs/feed
     */
    getCostFeed: (query: GetCostFeedParams = {}, params: RequestParams = {}) =>
      this.request<CostRead | null, HTTPValidationError>({
        path: `/api/costs/feed`,
        method: "GET",
        query: query,
        format: "json",
        ...params,
      }),

    /**
     * @description Требует сессии. Пользователь определяется по Redis; ID карточки не передаётся.
     *
     * @tags costs
     * @name GetCostDraft
     * @summary Свой черновик
     * @request GET:/api/costs/draft
     * @secure
     */
    getCostDraft: (params: RequestParams = {}) =>
      this.request<CostRead | null, void>({
        path: `/api/costs/draft`,
        method: "GET",
        secure: true,
        format: "json",
        ...params,
      }),

    /**
     * @description Три входных поля JSON: cost_description, cost_behavior и cost_code. Публикуется только собственный черновик. Статус published и дата формирования устанавливаются сервером.
     *
     * @tags costs
     * @name PublishCost
     * @summary Опубликовать свою издержку
     * @request PUT:/api/costs/{cost_id}
     * @secure
     */
    publishCost: (
      { costId }: PublishCostParams,
      data: CostPublish,
      params: RequestParams = {},
    ) =>
      this.request<CostRead, void | HTTPValidationError>({
        path: `/api/costs/${costId}`,
        method: "PUT",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Требует сессии и владения карточкой. Меняет статус на deleted; строка и файлы остаются.
     *
     * @tags costs
     * @name DeleteCost
     * @summary Логически удалить свою издержку
     * @request DELETE:/api/costs/{cost_id}
     * @secure
     */
    deleteCost: ({ costId }: DeleteCostParams, params: RequestParams = {}) =>
      this.request<void, void | HTTPValidationError>({
        path: `/api/costs/${costId}`,
        method: "DELETE",
        secure: true,
        ...params,
      }),

    /**
     * @description JSON is_liked: 1 — поставить, 0 — убрать. Пользователь берётся из Redis. Лайки разрешены только у опубликованных карточек.
     *
     * @tags costs
     * @name ChangeCostLike
     * @summary Поставить или убрать свой лайк
     * @request POST:/api/costs/{cost_id}/likes
     * @secure
     */
    changeCostLike: (
      { costId }: ChangeCostLikeParams,
      data: CostLikeChange,
      params: RequestParams = {},
    ) =>
      this.request<CostLikeRead, void | HTTPValidationError>({
        path: `/api/costs/${costId}/likes`,
        method: "POST",
        body: data,
        secure: true,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Сохраняет PBKDF2-хеш пароля. Сессию не создаёт.
     *
     * @tags users
     * @name RegisterUser
     * @summary Регистрация пользователя
     * @request POST:/api/users
     */
    registerUser: (data: UserRegister, params: RequestParams = {}) =>
      this.request<UserRead, void | HTTPValidationError>({
        path: `/api/users`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Проверяет пароль. Возвращает пользователя и Set-Cookie: cost_session. ID пользователя хранится в Redis в течение SESSION_TTL_SECONDS.
     *
     * @tags users
     * @name AuthenticateUser
     * @summary Вход и создание cookie-сессии
     * @request POST:/api/users/auth
     */
    authenticateUser: (data: UserCredentials, params: RequestParams = {}) =>
      this.request<UserRead, void | HTTPValidationError>({
        path: `/api/users/auth`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Удаляет сессию из Redis и cookie из браузера. Повторный выход допустим.
     *
     * @tags users
     * @name LogoutUser
     * @summary Выход и удаление сессии
     * @request POST:/api/users/logout
     * @secure
     */
    logoutUser: (params: RequestParams = {}) =>
      this.request<void, any>({
        path: `/api/users/logout`,
        method: "POST",
        secure: true,
        ...params,
      }),
  };
}
