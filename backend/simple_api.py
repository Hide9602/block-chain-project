"""
Simplified MetaSleuth API for demonstration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random
from datetime import datetime, timedelta

app = FastAPI(title="MetaSleuth NextGen API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "MetaSleuth NextGen API is running", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Models
class Node(BaseModel):
    id: str
    address: str
    nodeType: str
    label: Optional[str] = None
    balance: float
    riskLevel: str
    isSanctioned: bool

class Edge(BaseModel):
    id: str
    source: str
    target: str
    amount: float
    timestamp: str
    txHash: str
    isSuspicious: bool

class GraphResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class Pattern(BaseModel):
    pattern_id: str
    pattern_type: str
    confidence: float
    description: str
    evidence: List[str]
    severity: str

class RiskAssessment(BaseModel):
    overall_score: int
    risk_level: str
    factors: List[Dict[str, Any]]

class AnalysisRequest(BaseModel):
    address: str
    depth: int = 3
    include_patterns: bool = True
    include_anomalies: bool = True
    include_risk_score: bool = True
    include_narrative: bool = True
    language: str = "en"  # "en" or "ja"

class AnalysisResponse(BaseModel):
    patterns: Optional[List[Pattern]] = None
    risk_assessment: Optional[RiskAssessment] = None
    narrative: Optional[str] = None

# Helper functions
def generate_sample_nodes(center_address: str, count: int = 5) -> List[Node]:
    """Generate sample nodes for graph"""
    node_types = ['wallet', 'exchange', 'mixer', 'contract']
    risk_levels = ['none', 'low', 'medium', 'high']
    labels = {
        'exchange': ['Binance', 'Coinbase', 'Kraken', 'FTX', 'Huobi'],
        'mixer': ['Tornado Cash', 'ChipMixer', 'Wasabi Wallet'],
        'contract': ['Uniswap', 'Aave', 'Compound', 'MakerDAO']
    }
    
    nodes = [
        Node(
            id=f"node-0",
            address=center_address,
            nodeType='wallet',
            balance=round(random.uniform(1, 100), 2),
            riskLevel=random.choice(risk_levels),
            isSanctioned=False
        )
    ]
    
    for i in range(1, count):
        node_type = random.choice(node_types)
        label = None
        if node_type in labels:
            label = random.choice(labels[node_type])
        
        nodes.append(Node(
            id=f"node-{i}",
            address=f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
            nodeType=node_type,
            label=label,
            balance=round(random.uniform(10, 5000), 2),
            riskLevel=random.choice(risk_levels),
            isSanctioned=(node_type == 'mixer' and random.random() > 0.5)
        ))
    
    return nodes

def generate_sample_edges(nodes: List[Node]) -> List[Edge]:
    """Generate sample edges between nodes with tree-like structure"""
    if len(nodes) == 0:
        return []
    
    edges = []
    base_time = datetime.now() - timedelta(days=30)
    
    # Create a tree-like structure for better visualization
    # Connect each node to the root or previous nodes
    for i in range(1, len(nodes)):
        # Connect to root or previous node
        if i == 1:
            source_idx = 0
        else:
            # 70% chance to connect to root, 30% to previous nodes
            if random.random() < 0.7:
                source_idx = 0
            else:
                source_idx = random.randint(0, i - 1)
        
        target_idx = i
        
        timestamp = (base_time + timedelta(days=random.randint(0, 30))).isoformat()
        is_suspicious = nodes[source_idx].riskLevel in ['high', 'medium'] or \
                       nodes[target_idx].riskLevel in ['high', 'medium']
        
        edges.append(Edge(
            id=f"edge-{i-1}",
            source=nodes[source_idx].id,
            target=nodes[target_idx].id,
            amount=round(random.uniform(0.1, 50), 4),
            timestamp=timestamp,
            txHash=f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
            isSuspicious=is_suspicious
        ))
    
    # Add some additional connections for complexity (but not too many)
    additional_edges = min(2, len(nodes) // 3)
    for i in range(additional_edges):
        source_idx = random.randint(1, len(nodes) - 1)
        target_idx = random.randint(1, len(nodes) - 1)
        if source_idx != target_idx:
            timestamp = (base_time + timedelta(days=random.randint(0, 30))).isoformat()
            edges.append(Edge(
                id=f"edge-extra-{i}",
                source=nodes[source_idx].id,
                target=nodes[target_idx].id,
                amount=round(random.uniform(0.1, 20), 4),
                timestamp=timestamp,
                txHash=f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
                isSuspicious=random.random() > 0.6
            ))
    
    return edges

def generate_sample_patterns() -> List[Pattern]:
    """Generate sample fraud patterns"""
    pattern_types = [
        ("Money Laundering", "high", "Multiple transactions through mixer services detected"),
        ("Ponzi Scheme", "high", "Typical pyramid-like fund distribution pattern identified"),
        ("Phishing", "medium", "Address linked to known phishing campaigns"),
        ("Wash Trading", "medium", "Self-trading pattern detected across multiple wallets"),
    ]
    
    patterns = []
    for i, (ptype, severity, desc) in enumerate(random.sample(pattern_types, min(2, len(pattern_types)))):
        patterns.append(Pattern(
            pattern_id=f"pattern-{i}",
            pattern_type=ptype,
            confidence=round(random.uniform(0.6, 0.95), 2),
            description=desc,
            evidence=[
                f"Transaction to sanctioned address",
                f"High frequency trading pattern",
                f"Funds split across {random.randint(5, 20)} addresses"
            ],
            severity=severity
        ))
    
    return patterns

def generate_risk_assessment() -> RiskAssessment:
    """Generate sample risk assessment"""
    score = random.randint(30, 85)
    if score > 70:
        level = "High Risk"
    elif score > 40:
        level = "Medium Risk"
    else:
        level = "Low Risk"
    
    return RiskAssessment(
        overall_score=score,
        risk_level=level,
        factors=[
            {"name": "Mixer Interaction", "impact": "High", "score": random.randint(10, 30)},
            {"name": "Transaction Frequency", "impact": "Medium", "score": random.randint(5, 15)},
            {"name": "Sanctioned Entities", "impact": "High", "score": random.randint(15, 25)},
            {"name": "Address Age", "impact": "Low", "score": random.randint(0, 10)},
        ]
    )

def generate_narrative(address: str, patterns: List[Pattern], risk: RiskAssessment, language: str = "en") -> str:
    """Generate investigation narrative in specified language"""
    
    if language == "ja":
        # Japanese version
        risk_level_desc = "重大な" if risk.overall_score > 70 else "中程度の" if risk.overall_score > 40 else "低い"
        
        narrative = f"""
調査レポート
アドレス: {address}
生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
総合リスクスコア: {risk.overall_score}/100 ({risk.risk_level})

要約:
調査対象のブロックチェーンアドレスは、トランザクションパターン分析とエンティティ関連付けマッピングに基づき、{risk_level_desc}リスク指標を示しています。

検出されたパターン:
"""
        
        for i, pattern in enumerate(patterns, 1):
            narrative += f"""
{i}. {pattern.pattern_type} (信頼度: {int(pattern.confidence * 100)}%)
   - {pattern.description}
   - 深刻度: {pattern.severity.upper()}
   - 主な証拠: {', '.join(pattern.evidence[:2])}
"""
        
        narrative += f"""

リスク要因:
リスク評価に寄与する主な要因は以下の通りです:
"""
        for factor in risk.factors:
            narrative += f"- {factor['name']}: {factor['impact']}影響 (スコア: {factor['score']})\n"
        
        recommendation = ""
        if risk.overall_score > 70:
            recommendation = "高リスクスコアを考慮し、強化されたデューデリジェンスと関連当局への報告を推奨します。"
        elif risk.overall_score > 40:
            recommendation = "定期的な再評価を伴う標準的な監視手順を推奨します。"
        else:
            recommendation = "低リスクプロファイル。標準的なコンプライアンス手順が適用されます。"
        
        narrative += f"""

推奨事項:
{recommendation}

結論:
本分析は、ブロックチェーンアドレスのアクティビティパターン、関連リスク、および現行のインテリジェンスとパターン認識アルゴリズムに基づく推奨アクションの包括的な概要を提供します。
"""
    else:
        # English version
        risk_level_desc = "significant" if risk.overall_score > 70 else "moderate" if risk.overall_score > 40 else "low"
        
        narrative = f"""
INVESTIGATION REPORT
Address: {address}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Overall Risk Score: {risk.overall_score}/100 ({risk.risk_level})

EXECUTIVE SUMMARY:
The investigated blockchain address exhibits {risk_level_desc} risk indicators based on transaction pattern analysis and entity association mapping.

DETECTED PATTERNS:
"""
        
        for i, pattern in enumerate(patterns, 1):
            narrative += f"""
{i}. {pattern.pattern_type} (Confidence: {int(pattern.confidence * 100)}%)
   - {pattern.description}
   - Severity: {pattern.severity.upper()}
   - Key Evidence: {', '.join(pattern.evidence[:2])}
"""
        
        narrative += f"""

RISK FACTORS:
The primary contributing factors to the risk assessment include:
"""
        for factor in risk.factors:
            narrative += f"- {factor['name']}: {factor['impact']} impact (Score: {factor['score']})\n"
        
        recommendation = ""
        if risk.overall_score > 70:
            recommendation = "Given the high risk score, we recommend enhanced due diligence and potential reporting to relevant authorities."
        elif risk.overall_score > 40:
            recommendation = "Standard monitoring procedures are recommended with periodic reassessment."
        else:
            recommendation = "Low risk profile. Standard compliance procedures apply."
        
        narrative += f"""

RECOMMENDATIONS:
{recommendation}

CONCLUSION:
This analysis provides a comprehensive overview of the blockchain address activity patterns, associated risks, and recommended actions based on current intelligence and pattern recognition algorithms.
"""
    
    return narrative.strip()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "MetaSleuth NextGen API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/graph/address/{address}")
async def get_address_graph(address: str, depth: int = 3) -> GraphResponse:
    """Get transaction graph for an address"""
    # Normalize address: add 0x prefix if missing
    if not address.startswith("0x"):
        address = "0x" + address
    
    if len(address) < 10:
        raise HTTPException(status_code=400, detail="Invalid address format")
    
    nodes = generate_sample_nodes(address, count=min(depth * 2, 8))
    edges = generate_sample_edges(nodes)
    
    return GraphResponse(nodes=nodes, edges=edges)

@app.post("/api/v1/ml/analyze")
async def analyze_address(request: AnalysisRequest) -> AnalysisResponse:
    """Perform ML analysis on address"""
    # Normalize address: add 0x prefix if missing
    if not request.address.startswith("0x"):
        request.address = "0x" + request.address
    
    if len(request.address) < 10:
        raise HTTPException(status_code=400, detail="Invalid address format")
    
    response = AnalysisResponse()
    
    if request.include_patterns:
        response.patterns = generate_sample_patterns()
    
    if request.include_risk_score:
        response.risk_assessment = generate_risk_assessment()
    
    if request.include_narrative and response.patterns and response.risk_assessment:
        response.narrative = generate_narrative(
            request.address, 
            response.patterns, 
            response.risk_assessment,
            request.language
        )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
