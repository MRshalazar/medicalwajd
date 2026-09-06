use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ProofRequest {
    pub value: u64,
    pub min: u64,
    pub max: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProofResponse {
    pub success: bool,
    pub proof: String,
    pub commitment: String,
    pub message: String,
}