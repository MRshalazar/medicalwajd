use std::fmt;

#[derive(Debug)]
pub enum ZKPError {
    InvalidRange,
    ProofGenerationFailed,
    ProofVerificationFailed,
}

impl fmt::Display for ZKPError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ZKPError::InvalidRange => write!(f, "Invalid range"),
            ZKPError::ProofGenerationFailed => write!(f, "Proof generation failed"),
            ZKPError::ProofVerificationFailed => write!(f, "Proof verification failed"),
        }
    }
}

impl std::error::Error for ZKPError {}