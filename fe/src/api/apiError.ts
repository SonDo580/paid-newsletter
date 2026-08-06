interface ErrResBody {
  message: string;
  detail?: unknown;
}

export class ApiError extends Error {
  readonly status: number;
  readonly data: ErrResBody;

  constructor(status: number, data: ErrResBody) {
    super(data.message);
    this.name = "ApiError";
    this.status = status;
    this.data = data; // not use yet
  }
}

export function getApiErrMsg(err: unknown): string {
  if (!(err instanceof ApiError)) {
    return "An unexpected error occurred. Please try again.";
  }
  return err.message;
}
