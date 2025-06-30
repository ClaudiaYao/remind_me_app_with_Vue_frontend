export enum CognitoErrorCode {
  EmailNotVerified = "EmailNotVerifiedException",
  NotAuthorized = "NotAuthorizedException",
  UserNotFound = "UserNotFoundException",
  UserNotConfirmed = "UserNotConfirmedException",
  PasswordResetRequired = "PasswordResetRequiredException",
  CodeMismatch = "CodeMismatchException",
  ExpiredCode = "ExpiredCodeException",
  InvalidParameter = "InvalidParameterException",
}

export class CognitoAuthError extends Error {
  code: CognitoErrorCode;

  constructor(code: CognitoErrorCode, message?: string) {
    super(message || code);
    this.name = "CognitoAuthError";
    this.code = code;
  }
}
