// src/services/userPool.ts
import { CognitoUserPool } from "amazon-cognito-identity-js";
import { cognitoConfig } from "@/config/cognitoConfig";

export const userPool = new CognitoUserPool({
  UserPoolId: cognitoConfig.userPoolId,
  ClientId: cognitoConfig.clientId,
});
