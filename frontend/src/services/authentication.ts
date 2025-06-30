import {
  CognitoUser,
  AuthenticationDetails,
  CognitoUserSession,
  CognitoUserAttribute,
} from "amazon-cognito-identity-js";

import { API_BASE_URL } from "@/config/config";
import { CognitoErrorCode, CognitoAuthError } from "@/services/appExceptions";

// The purpose of the authenticateUser function is to wrap the callback-based Cognito authentication process in a Promise,
// making it easier to use with async/await syntax in modern JavaScript/TypeScript.
export const authenticateUser = async (
  cognitoUser: CognitoUser,
  authenticationDetails: AuthenticationDetails
): Promise<CognitoUserSession> => {
  return new Promise((resolve, reject) => {
    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: (session) => {
        resolve(session);
      },
      onFailure: (err) => {
        const code = err.code as CognitoErrorCode;
        if (Object.values(CognitoErrorCode).includes(code)) {
          reject(new CognitoAuthError(code, err.message));
        } else {
          reject(err); // fallback for unknown errors
        }
      },
    });
  });
};

const getUserAttributes = async (cognitoUser: CognitoUser): Promise<CognitoUserAttribute[]> => {
  return new Promise((resolve, reject) => {
    console.log(cognitoUser);
    cognitoUser.getUserAttributes((err, attributes) => {
      if (err) {
        console.error("Error fetching user attributes:", err);
        reject(new Error(err.message || "Error fetching user attributes"));
      } else {
        if (attributes) {
          resolve(attributes);
        } else {
          reject(new Error("No attributes returned"));
        }
      }
    });
  });
};

export const isEmailVerified = async (cognitoUser: CognitoUser): Promise<boolean> => {
  try {
    const userAttributes = await getUserAttributes(cognitoUser);
    console.log(userAttributes);
    // Check if email is verified
    const emailVerified = userAttributes.some((attr) => attr.Name === "email_verified" && attr.Value === "true");
    return emailVerified;
  } catch {
    throw new CognitoAuthError(CognitoErrorCode.EmailNotVerified, "User email not verified!");
  }
};

export const notifyBackendLogin = async (token: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/user/login`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Unauthorized: Token may be invalid.");
    } else if (response.status === 500) {
      throw new Error("Server error during login.");
    } else {
      throw new Error(`Login failed with status: ${response.status}`);
    }
  }
};

export const notifyBackendLogout = async (token: string): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      console.warn("Logout request failed with status:", response.status);
    }
  } catch (error) {
    console.error("Error notifying backend about logout:", error);
  }
};
