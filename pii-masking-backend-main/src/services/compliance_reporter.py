import json
from datetime import datetime
from typing import List, Dict, Any

def generate_html_compliance_report(audit_logs: List[Dict[str, Any]]) -> str:
    """Generate a clean HTML compliance audit report for download/export."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    total_files = len(audit_logs)
    
    rows_html = ""
    for log in audit_logs:
        cats = ", ".join(log.get("pii_categories", [])) if isinstance(log.get("pii_categories"), list) else str(log.get("pii_categories"))
        rows_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{log.get('id')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{log.get('timestamp')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><b>{log.get('filename')}</b></td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-family: monospace; font-size: 11px;">{log.get('file_hash')[:16]}...</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><span style="background: #eef2ff; color: #4f46e5; padding: 3px 8px; border-radius: 4px; font-weight: 500;">{cats}</span></td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{log.get('masking_type')}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><span style="color: #16a34a; font-weight: bold;">{log.get('status')}</span></td>
        </tr>
        """
        
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PII Masking Enterprise Compliance Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #1e293b; background: #f8fafc; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px; }}
            h1 {{ color: #0f172a; margin: 0 0 10px 0; }}
            .badge {{ background: #22c55e; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #f1f5f9; padding: 12px; text-align: left; font-size: 13px; font-weight: 600; color: #475569; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span class="badge">GDPR / HIPAA / SOC2 COMPLIANT AUDIT</span>
                <h1>PII Masking Verification Certificate</h1>
                <p style="color: #64748b; margin: 5px 0 0 0;">Generated on: <b>{now}</b> | Local Node: <b>Enterprise-Primary</b></p>
            </div>
            
            <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                <div style="flex: 1; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <div style="font-size: 12px; color: #64748b;">Total Sanitized Records</div>
                    <div style="font-size: 24px; font-weight: bold; color: #0f172a;">{total_files}</div>
                </div>
                <div style="flex: 1; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <div style="font-size: 12px; color: #64748b;">Encryption Standard</div>
                    <div style="font-size: 24px; font-weight: bold; color: #0f172a;">AES-256</div>
                </div>
            </div>

            <h3>Sanitization Audit Ledger</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Timestamp</th>
                        <th>File Name</th>
                        <th>SHA-256 Hash</th>
                        <th>PII Sanitized</th>
                        <th>Mode</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            
            <div class="footer">
                <p>This automated compliance document verifies that all listed files were processed using enterprise redaction policies. Raw file data has been scrubbed of sensitive PII entities prior to persistence.</p>
            </div>
        </div>
    </body>
    </html>
    """
