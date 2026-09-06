use std::fmt;

#[derive(Debug)]
pub enum ZKPError {
    ProofGenerationFailed,
    ProofVerificationFailed,
}

impl fmt::Display for ZKPError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ZKPError::ProofGenerationFailed => write!(f, "Proof generation failed"),
            ZKPError::ProofVerificationFailed => write!(f, "Proof verification failed"),
        }
    }
}

impl std::error::Error for ZKPError {}