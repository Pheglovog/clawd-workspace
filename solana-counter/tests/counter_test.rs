// Solana 计数器测试
// 使用 solana-program-test 库进行单元测试

use solana_program::program_error::ProgramError;
use solana_program_test::*;
use solana_sdk::{
    pubkey::Pubkey,
    signature::{Keypair, Signer},
};
use counter::{
    state::Counter,
    instruction::CounterInstruction,
    CounterError,
    error::CounterError as CounterProgramError,
};

const PROGRAM_ID: &str = "COUNTER_PROGRAM_ID"; // 部署后替换为实际程序 ID

fn get_program_id() -> Pubkey {
    Pubkey::new_from_str(PROGRAM_ID).unwrap()
}

#[tokio::test]
async fn test_initialize_counter() {
    let program_id = get_program_id();

    // 创建账户
    let payer = Keypair::new();
    let signer = Keypair::new();

    let (mut banks_client, payer_key, recent_blockhash) =
        ProgramTestBanksClient::new(Some(*payer.key())).await;

    let mut client = banks_client;

    // 初始化计数器
    let counter_pda = Pubkey::new_unique();
    let counter_account = solana_sdk::account::Account::new(&counter_pda, &program_id, false);

    let instruction = CounterInstruction::Initialize;

    let transaction = Transaction::new_signed_with_payer(
        &[payer_key, signer],
        vec![instruction.into()],
        Some(&program_id),
        &[counter_account],
        Some(&payer.pubkey()),
    );

    client.send_transaction(&mut recent_blockhash, &transaction).await.unwrap();
}

#[tokio::test]
async fn test_increment_counter() {
    let program_id = get_program_id();

    // 创建账户
    let payer = Keypair::new();
    let signer = Keypair::new();

    let (mut banks_client, payer_key, recent_blockhash) =
        ProgramTestBanksClient::new(Some(*payer.key())).await;

    let mut client = banks_client;

    // 确保计数器已经初始化
    let counter_pda = Pubkey::new_unique();
    let counter_account = solana_sdk::account::Account::new(&counter_pda, &program_id, false);

    let (mut banks_client, payer_key, recent_blockhash) =
        ProgramTestBanksClient::new(Some(*payer.key())).await;

    let mut client = banks_client;

    // 增加计数器
    let instruction = CounterInstruction::Increment;

    let transaction = Transaction::new_signed_with_payer(
        &[payer_key, signer],
        vec![instruction.into()],
        Some(&program_id),
        &[counter_account],
        Some(&payer.pubkey()),
    );

    client.send_transaction(&mut recent_blockhash, &transaction).await.unwrap();
}

#[tokio::test]
async fn test_decrement_counter() {
    let program_id = get_program_id();

    // 创建账户
    let payer = Keypair::new();
    let signer = Keypair::new();

    let (mut banks_client, payer_key, recent_blockhash) =
        ProgramTestBanksClient::new(Some(*payer.key())).await;

    let mut client = banks_client;

    // 确保计数器已经初始化到 > 0
    let counter_pda = Pubkey::new_unique();
    let counter_account = solana_sdk::account::Account::new(&counter_pda, &program_id, false);

    // 首先设置计数器为 1
    let set_instruction = CounterInstruction::Set { count: 1 };

    let transaction = Transaction::new_signed_with_payer(
        &[payer_key, signer],
        vec![set_instruction.into()],
        Some(&program_id),
        &[counter_account],
        Some(&payer.pubkey()),
    );

    client.send_transaction(&mut recent_blockhash, &transaction).await.unwrap();

    // 等待交易确认
    // 实际测试中需要添加 sleep 或等待机制

    // 减少计数器
    let decrement_instruction = CounterInstruction::Decrement;

    let transaction = Transaction::new_signed_with_payer(
        &[payer_key, signer],
        vec![decrement_instruction.into()],
        Some(&program_id),
        &[counter_account],
        Some(&payer.pubkey()),
    );

    client.send_transaction(&mut recent_blockhash, &transaction).await.unwrap();
}

#[tokio::test]
async fn test_set_counter() {
    let program_id = get_program_id();

    // 创建账户
    let payer = Keypair::new();
    let signer = Keypair::new();

    let (mut banks_client, payer_key, recent_blockhash) =
        ProgramTestBanksClient::new(Some(*payer.key())).await;

    let mut client = banks_client;

    let counter_pda = Pubkey::new_unique();
    let counter_account = solana_sdk::account::Account::new(&counter_pda, &program_id, false);

    // 设置计数器为特定值
    let set_instruction = CounterInstruction::Set { count: 42 };

    let transaction = Transaction::new_signed_with_payer(
        &[payer_key, signer],
        vec![set_instruction.into()],
        Some(&program_id),
        &[counter_account],
        Some(&payer.pubkey()),
    );

    client.send_transaction(&mut recent_blockhash, &transaction).await.unwrap();
}

#[tokio::test]
async fn test_close_counter() {
    let program_id = get_program_id();

    // 创建账户
    let payer = Keypair::new();
    let signer = Keypair::new();

    let (mut banks_client, payer_key, recent_blockhash) =
        ProgramTestBanksClient::new(Some(*payer.key())).await;

    let mut client = banks_client;

    let counter_pda = Pubkey::new_unique();
    let counter_account = solana_sdk::account::Account::new(&counter_pda, &program_id, false);

    // 首先初始化计数器
    let init_instruction = CounterInstruction::Initialize;

    let transaction = Transaction::new_signed_with_payer(
        &[payer_key, signer],
        vec![init_instruction.into()],
        Some(&program_id),
        &[counter_account],
        Some(&payer.pubkey()),
    );

    client.send_transaction(&mut recent_blockhash, &transaction).await.unwrap();

    // 关闭计数器（释放租金）
    let close_instruction = CounterInstruction::Close;

    let transaction = Transaction::new_signed_with_payer(
        &[payer_key, signer],
        vec![close_instruction.into()],
        Some(&program_id),
        &[counter_account],
        Some(&payer.pubkey()),
    );

    client.send_transaction(&mut recent_blockhash, &transaction).await.unwrap();
}
