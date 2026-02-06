// Solana 计数器指令处理器
// 处理所有指令并更新 Counter 状态

use solana_program::{
    account_info::{next_account_info, AccountInfo},
    borsh::BorshSerialize,
    entrypoint,
    program_error::ProgramError,
    msg,
    program::set_return_data,
    pubkey::Pubkey,
    sysvar::{clock::Clock, rent::Rent},
    system_program::{self, System},
};
use solana_security::exitpreprogram::{self, exit};

use counter::{
    error::CounterError,
    instruction::{CounterInstruction, Initialize, Increment, Decrement, Set, Reset, Close},
    state::{Counter, Signer},
};

// 程序 ID（编译后替换）
solana_program::declare_id!("COUNTER_PROGRAM_ID");

#[derive(Debug)]
pub struct Context<'a, 'b, 'info> {
    pub program_id: &'a Pubkey,
    pub accounts: InitializeAccounts<'info, 'b>,
    pub system: AccountInfo<'info, System>,
}

impl<'a, 'b, 'info> Context<'a, 'b, 'info> {
    pub fn new(program_id: &'a Pubkey, accounts: InitializeAccounts<'info, 'b>) -> Self {
        Self {
            program_id,
            accounts,
            system: accounts.system,
        }
    }
}

#[derive(Accounts)]
pub struct InitializeAccounts<'info, 'b> {
    #[account(init, payer, seeds = [b"counter"], bump)]
    pub counter: AccountInfo<'info, Counter>,
    #[account(mut, seeds = [b"counter", b"signer"])]
    pub signer: AccountInfo<'info, Signer>,
    #[account(init, seeds = [b"counter"], b"signer"], bump)]
    pub pda: AccountInfo<'info, Signer>,
    #[account(
        init,
        seeds = [b"counter"],
        bump
    )]
    pub bump: AccountInfo<'info, Signer>,
    #[account(init)]
    pub system: AccountInfo<'info, System>,
}

// 增加计数器
#[derive(Accounts)]
pub struct IncrementAccounts<'info, 'b> {
    #[account(mut, seeds = [b"counter"], b"signer"])]
    pub counter: AccountInfo<'info, Counter>,
    #[account(signer)]
    pub signer: AccountInfo<'info, Signer>,
}

// 减少计数器
#[derive(Accounts)]
pub struct DecrementAccounts<'info, 'b> {
    #[account(mut, seeds = [b"counter"], b"signer"])]
    pub counter: AccountInfo<'info, Counter>,
    #[account(signer)]
    pub signer: AccountInfo<'info, Signer>,
}

// 设置计数器
#[derive(Accounts)]
pub struct SetAccounts<'info, 'b> {
    #[account(mut, seeds = [b"counter"], b"signer"])]
    pub counter: AccountInfo<'info, Counter>,
    #[account(signer)]
    pub signer: AccountInfo<'info, Signer>,
}

// 重置计数器
#[derive(Accounts)]
pub struct ResetAccounts<'info, 'b> {
    #[account(mut, seeds = [b"counter"], b"signer"])]
    pub counter: AccountInfo<'info, Counter>,
    #[account(signer)]
    pub signer: AccountInfo<'info, Signer>,
}

// 关闭计数器
#[derive(Accounts)]
pub struct CloseAccounts<'info, 'b> {
    #[account(mut, seeds = [b"counter"], bump)]
    pub counter: AccountInfo<'info, Counter>,
    #[account(init)]
    pub pda: AccountInfo<'info, Signer>,
    #[account(mut)]
    pub signer: AccountInfo<'info, Signer>,
}

// 处理 Initialize 指令
pub fn process_initialize<'a, 'b, 'info>(
    ctx: Context<'a, 'b, 'info>,
    _instruction: Initialize,
) -> Result<(), CounterError> {
    // 检查 bump 是否为 0
    if ctx.accounts.bump.bump != 0 {
        return Err(CounterError::AlreadyInitialized);
    }

    // 初始化计数器
    let counter = &mut ctx.accounts.counter.data;
    *counter = Counter { count: 0 };

    // 设置 bump
    ctx.accounts.bump.bump = ctx.accounts.bump.bump;

    msg!("Counter initialized");
    Ok(())
}

// 处理 Increment 指令
pub fn process_increment<'a, 'b, 'info>(
    ctx: Context<'a, 'b, 'info>,
    _instruction: Increment,
) -> Result<(), CounterError> {
    let counter = &mut ctx.accounts.counter.data;

    // 增加计数器
    counter.add(1)?;

    msg!("Incremented counter to {}", counter.get_value()?);

    Ok(())
}

// 处理 Decrement 指令
pub fn process_decrement<'a, 'b, 'info>(
    ctx: Context<'a, 'b, 'info>,
    _instruction: Decrement,
) -> Result<(), CounterError> {
    let counter = &mut ctx.accounts.counter.data;

    // 减少计数器
    counter.sub(1)?;

    msg!("Decremented counter to {}", counter.get_value()?);

    Ok(())
}

// 处理 Set 指令
pub fn process_set<'a, 'b, 'info>(
    ctx: Context<'a, 'b, 'info>,
    instruction: Set,
) -> Result<(), CounterError> {
    let counter = &mut ctx.accounts.counter.data;

    // 设置计数器
    counter.set(instruction.value)?;

    msg!("Set counter to {}", counter.get_value()?);

    Ok(())
}

// 处理 Reset 指令
pub fn process_reset<'a, 'b, 'info>(
    ctx: Context<'a, 'b, 'info>,
    _instruction: Reset,
) -> Result<(), CounterError> {
    let counter = &mut ctx.accounts.counter.data;

    // 重置计数器
    counter.reset()?;

    msg!("Reset counter to 0");

    Ok(())
}

// 处理 Close 指令
pub fn process_close<'a, 'b, 'info>(
    ctx: Context<'a, 'b, 'info>,
    _instruction: Close,
) -> Result<(), CounterError> {
    // 关闭账户，释放租金
    let counter_data = ctx.accounts.counter.data;
    let counter_lamports = ctx.accounts.counter.lamports();

    // 检查是否有足够的租金退还
    if counter_lamports > 0 {
        // 将余额转回给 payer
        **ctx.accounts.signer.try_borrow_mut_lamports() -= counter_lamports;
        ctx.accounts.system.transfer(
            ctx.accounts.signer.try_borrow_mut_lamports(),
            ctx.accounts.counter.to_account_info(),
            counter_lamports,
        )?;
    }

    msg!("Closed counter account");

    Ok(())
}

// 入口点
entrypoint!(process_instruction);

pub fn process_instruction<'a, 'b, 'info>(
    program_id: &'a Pubkey,
    accounts: &'b [AccountInfo<'info, 'b>],
    data: &[u8],
) -> u64 {
    // 将数据解析为指令
    let instruction = CounterInstruction::try_from_slice(data)
        .map_err(|_| {
            msg!("Invalid instruction");
            1
        })
        .expect("Failed to parse instruction");

    // 创建上下文
    let ctx = Context::new(program_id, accounts);

    // 处理指令
    match instruction {
        CounterInstruction::Initialize => {
            // 解析指令参数
            let instruction_data = &data[1..];

            // 处理初始化
            match process_initialize(ctx, instruction_data) {
                Ok(_) => 0,
                Err(e) => {
                    msg!("Initialize failed: {}", e);
                    1
                }
            }
        }
        CounterInstruction::Increment => {
            // 获取 IncrementAccounts
            let mut accounts = InitializeAccounts::try_from_slice(accounts)
                .expect("Failed to deserialize accounts");

            match process_increment(ctx, instruction) {
                Ok(_) => 0,
                Err(e) => {
                    msg!("Increment failed: {}", e);
                    1
                }
            }
        }
        CounterInstruction::Decrement => {
            // 获取 DecrementAccounts
            let mut accounts = InitializeAccounts::try_from_slice(accounts)
                .expect("Failed to deserialize accounts");

            match process_decrement(ctx, instruction) {
                Ok(_) => 0,
                Err(e) => {
                    msg!("Decrement failed: {}", e);
                    1
                }
            }
        }
        CounterInstruction::Set { value } => {
            // 获取 SetAccounts
            let mut accounts = InitializeAccounts::try_from_slice(accounts)
                .expect("Failed to deserialize accounts");

            match process_set(ctx, instruction) {
                Ok(_) => 0,
                Err(e) => {
                    msg!("Set failed: {}", e);
                    1
                }
            }
        }
        CounterInstruction::Reset => {
            // 获取 ResetAccounts
            let mut accounts = InitializeAccounts::try_from_slice(accounts)
                .expect("Failed to deserialize accounts");

            match process_reset(ctx, instruction) {
                Ok(_) => 0,
                Err(e) => {
                    msg!("Reset failed: {}", e);
                    1
                }
            }
        }
        CounterInstruction::Close => {
            // 获取 CloseAccounts
            let mut accounts = CloseAccounts::try_from_slice(accounts)
                .expect("Failed to deserialize accounts");

            match process_close(ctx, instruction) {
                Ok(_) => 0,
                Err(e) => {
                    msg!("Close failed: {}", e);
                    1
                }
            }
        }
    }
}
