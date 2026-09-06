mod range;

use serde::{Deserialize, Serialize};
use std::io::{self, Read};

#[derive(Deserialize)]
struct Input {
    value: u64,
    min: u64,
    max: u64,
}

#[derive(Serialize)]
struct Output {
    verified: bool,
    status: String,
    proof_type: String,
}

fn main() {

    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();

    let req: Input = serde_json::from_str(&input).unwrap();

    let verified = range::prove_bp(req.value);

    let status = if verified {
        if req.value >= req.min && req.value <= req.max {
            "NORMAL"
        } else {
            "ALERT"
        }
    } else {
        "PROOF_FAILED"
    };

    let response = Output {
        verified,
        status: status.to_string(),
        proof_type: "Bulletproofs".to_string(),
    };

    println!("{}", serde_json::to_string(&response).unwrap());

}