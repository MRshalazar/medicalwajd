use bulletproofs::{BulletproofGens, PedersenGens, RangeProof};

use curve25519_dalek_ng::scalar::Scalar;

use merlin::Transcript;

use rand::thread_rng;

pub fn prove_bp(value: u64) -> bool {

    let pc_gens = PedersenGens::default();

    let bp_gens = BulletproofGens::new(64, 1);

    let blinding = Scalar::random(&mut thread_rng());

    let mut prover_transcript =
        Transcript::new(b"Privacy-CDSS");

    let (proof, commitment) =
        match RangeProof::prove_single(
            &bp_gens,
            &pc_gens,
            &mut prover_transcript,
            value,
            &blinding,
            64,
        ) {

            Ok(v) => v,

            Err(_) => return false,
        };

    let mut verifier_transcript =
        Transcript::new(b"Privacy-CDSS");

    proof
        .verify_single(
            &bp_gens,
            &pc_gens,
            &mut verifier_transcript,
            &commitment,
            64,
        )
        .is_ok()
}