import sys
import os

# Ensure src is in sys.path for offline pytest execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from anchor_sec_lint import AnchorSecLinter, analyze_code

def test_linter_detects_unchecked_account():
    code = """
    #[derive(Accounts)]
    pub struct UpdateSettings<'info> {
        #[account(mut)]
        pub user: Signer<'info>,
        pub arbitrary_data: UncheckedAccount<'info>,
    }
    """
    findings = analyze_code(code)
    assert len(findings) > 0
    rule_ids = [f["rule_id"] for f in findings]
    assert "SEC-001" in rule_ids
    assert findings[0]["severity"] == "HIGH"

def test_linter_detects_raw_account_info():
    code = """
    pub struct TransferFunds<'info> {
        pub receiver: AccountInfo<'info>,
    }
    """
    findings = analyze_code(code)
    assert len(findings) > 0
    rule_ids = [f["rule_id"] for f in findings]
    assert "SEC-002" in rule_ids
    assert any(f["severity"] == "CRITICAL" for f in findings)

def test_linter_clean_code():
    code = """
    #[derive(Accounts)]
    pub struct Initialize<'info> {
        #[account(init, payer = user, space = 8 + 32)]
        pub state: Account<'info, StateAccount>,
        #[account(mut)]
        pub user: Signer<'info>,
        pub system_program: Program<'info, System>,
    }
    """
    findings = analyze_code(code)
    # Clean code should trigger no severe security violations
    critical_or_high = [f for f in findings if f["severity"] in ("HIGH", "CRITICAL")]
    assert len(critical_or_high) == 0

def test_linter_manual_key_check():
    code = """
    pub fn handler(ctx: Context<Update>) -> Result<()> {
        require!(ctx.accounts.authority.key() != some_other_key, CustomError::Unauthorized);
        Ok(())
    }
    """
    findings = analyze_code(code)
    assert any(f["rule_id"] == "SEC-004" for f in findings)
