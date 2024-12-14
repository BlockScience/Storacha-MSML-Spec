import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional
import random
from enum import Enum
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeType(Enum):
    OSN = "Object Storage Node"
    RAN = "Retrieval Acceleration Node"
    IN = "Indexing Node"
    FN = "Fisherman Node"

@dataclass
class TokenAllocation:
    initial_contributors: float = 0.20  # 20%
    early_backers: float = 0.17        # 17%
    r_and_d: float = 0.20             # 20%
    ecosystem: float = 0.20           # 20%
    network_growth: float = 0.23      # 23%
    total_supply: int = 100_000_000_000  # 100B tokens
    
    # KPI-based minting parameters
    alpha: float = 0.6  # 60% of rewards are KPI-based
    w_osn: float = 0.4  # 40% to Object Storage Nodes
    w_ran: float = 0.3  # 30% to Retrieval Acceleration Nodes
    w_in: float = 0.2   # 20% to Indexing Nodes
    w_fn: float = 0.1   # 10% to Fisherman Nodes

@dataclass
class WorkMetrics:
    bytes_stored: float = 0.0
    bytes_read: float = 0.0
    indices_served: int = 0
    total_work_units: float = 0.0

@dataclass
class SessionParameters:
    storage_load_bytes: int
    read_rate_bps: int
    write_rate_bps: int
    duration_seconds: int
    request_frequency: float
    collateral: float

@dataclass
class NodeRequirements:
    min_stake: int
    target_ttfb_ms: float
    min_availability: float
    min_bandwidth_gbps: float = 1.0
    storage_capacity_tb: float = 10.0

class Node:
    def __init__(self, node_type: NodeType, stake: float):
        self.node_type = node_type
        self.stake = stake
        self.reputation = 1.0
        self.rewards = 0.0
        self.slashed = False
        self.work_metrics = WorkMetrics()
        self.performance_metrics = {
            'uptime': 1.0,
            'latency': 0.0,
            'successful_ops': 0,
            'storage_used': 0.0,  # in bytes
            'bytes_served': 0.0,
            'cache_hits': 0,
            'total_requests': 0
        }

    def update_performance(self, success_rate: float, latency: float):
        self.performance_metrics['uptime'] *= 0.95  # Decay factor
        self.performance_metrics['uptime'] += 0.05 * success_rate
        self.performance_metrics['latency'] = latency
        if self.node_type == NodeType.RAN:
            self.performance_metrics['cache_hits'] += random.randint(0, 100)
            self.performance_metrics['total_requests'] += 100
        self.reputation = self.calculate_reputation()

    def calculate_reputation(self) -> float:
        base_rep = (0.4 * self.performance_metrics['uptime'] +
                   0.4 * (1.0 - min(1.0, self.performance_metrics['latency'] / self.get_ttfb_target())) +
                   0.2 * (1.0 if not self.slashed else 0.0))

        if self.node_type == NodeType.RAN and self.performance_metrics['total_requests'] > 0:
            cache_hit_rate = self.performance_metrics['cache_hits'] / self.performance_metrics['total_requests']
            base_rep *= (1 + 0.2 * cache_hit_rate)  # Up to 20% bonus for good cache performance

        return min(1.0, base_rep)

    def get_ttfb_target(self) -> float:
        targets = {
            NodeType.OSN: 150.0,  # ms
            NodeType.RAN: 70.0,   # ms
            NodeType.IN: 100.0    # ms
        }
        return targets.get(self.node_type, 100.0)

    def update_work_metrics(self, epoch_duration: int):
        if self.node_type == NodeType.OSN:
            # Simulate storage work
            self.work_metrics.bytes_stored += self.performance_metrics['storage_used']
        elif self.node_type == NodeType.RAN:
            # Simulate retrieval work
            self.work_metrics.bytes_read += self.performance_metrics['bytes_served']
        elif self.node_type == NodeType.IN:
            # Simulate indexing work
            self.work_metrics.indices_served += self.performance_metrics['successful_ops']
        
        # Update total work units (normalized)
        self.work_metrics.total_work_units = (
            self.work_metrics.bytes_stored / 1e9 +  # Convert to GB
            self.work_metrics.bytes_read / 1e9 +    # Convert to GB
            self.work_metrics.indices_served / 1000  # Normalize indices
        )

    def calculate_required_pledge(self, circulating_supply: float) -> float:
        """Calculate minimum pledge based on circulating supply and work capacity"""
        base_requirement = {
            NodeType.OSN: 100000,
            NodeType.RAN: 75000,
            NodeType.IN: 50000,
            NodeType.FN: 25000
        }[self.node_type]
        
        # Scale with circulating supply and work units
        supply_factor = np.sqrt(circulating_supply / 1e9)  # Square root scaling
        work_factor = np.log1p(self.work_metrics.total_work_units)  # Logarithmic scaling
        
        return base_requirement * supply_factor * (1 + 0.1 * work_factor)

class StorachaSystem:
    def __init__(self):
        self.allocation = TokenAllocation()
        self.nodes: Dict[str, List[Node]] = {
            NodeType.OSN.name: [],
            NodeType.RAN.name: [],
            NodeType.IN.name: [],
            NodeType.FN.name: []
        }
        self.treasury_balance = 0.0
        self.circulating_supply = 0.0
        self.burnt_tokens = 0.0
        self.current_epoch = 0
        self.base_inflation_rate = 0.10  # Start at 10% max
        self.node_requirements = {
            NodeType.OSN: NodeRequirements(100000, 150.0, 0.999),
            NodeType.RAN: NodeRequirements(75000, 70.0, 0.999),
            NodeType.IN: NodeRequirements(50000, 100.0, 0.999),
            NodeType.FN: NodeRequirements(25000, float('inf'), 0.99)
        }
        # Session pricing constants
        self.Cs = 0.02  # $/GB/month for storage
        self.CR = 0.01  # $/GB for reads
        self.CW = 0.015 # $/GB for writes

    def add_node(self, node_type: NodeType, stake: float):
        if stake >= self.node_requirements[node_type].min_stake:
            node = Node(node_type, stake)
            self.nodes[node_type.name].append(node)
            logger.info(f"Added {node_type.name} with stake {stake}")
            return True
        return False

    def get_min_stake(self, node_type: NodeType) -> float:
        return self.node_requirements[node_type].min_stake

    def calculate_session_cost(self, params: SessionParameters) -> float:
        """Calculate session cost using the formula: P = T * (Cs*S + CR*R + CW*W)"""
        # Convert to GB and months
        storage_gb = params.storage_load_bytes / (1024 * 1024 * 1024)
        read_gb_per_month = (params.read_rate_bps * 3600 * 24 * 30) / (8 * 1024 * 1024 * 1024)
        write_gb_per_month = (params.write_rate_bps * 3600 * 24 * 30) / (8 * 1024 * 1024 * 1024)
        duration_months = params.duration_seconds / (30 * 24 * 3600)

        # Calculate base cost
        base_cost = duration_months * (
            self.Cs * storage_gb +
            self.CR * read_gb_per_month +
            self.CW * write_gb_per_month
        )

        # Apply network utilization adjustment
        utilization = self.calculate_network_utilization()
        market_adjustment = np.exp(2 * utilization) - 1

        # Apply request frequency scaling
        frequency_factor = np.log1p(params.request_frequency)

        final_cost = base_cost * (1 + market_adjustment) * (1 + 0.1 * frequency_factor)
        return final_cost

    def calculate_kpi_rewards(self, node_type: NodeType, node: Node) -> float:
        """Calculate KPI-based rewards for a node"""
        total_type_work = sum(n.work_metrics.total_work_units 
                            for n in self.nodes[node_type.name])
        if total_type_work == 0:
            return 0

        # Get weight for node type
        type_weight = {
            NodeType.OSN: self.allocation.w_osn,
            NodeType.RAN: self.allocation.w_ran,
            NodeType.IN: self.allocation.w_in,
            NodeType.FN: self.allocation.w_fn
        }[node_type]

        # Calculate KPI-based portion
        kpi_rewards = (self.allocation.total_supply * 
                      self.base_inflation_rate * 
                      self.allocation.alpha * 
                      type_weight * 
                      (node.work_metrics.total_work_units / total_type_work))

        return kpi_rewards

    def distribute_rewards(self):
        """Distribute rewards using both simple and KPI-based minting"""
        simple_rewards = (self.allocation.total_supply * 
                        self.base_inflation_rate * 
                        (1 - self.allocation.alpha) / 
                        (365 * 24))  # Hourly rewards

        for node_type in self.nodes:
            eligible_nodes = [node for node in self.nodes[node_type] if not node.slashed]
            if not eligible_nodes:
                continue

            # Distribute simple rewards
            type_allocation = simple_rewards * self.get_type_allocation(node_type)
            for node in eligible_nodes:
                node.rewards += type_allocation * (node.reputation / len(eligible_nodes))
                
                # Add KPI-based rewards
                node.rewards += self.calculate_kpi_rewards(NodeType[node_type], node)

    def verify_nodes(self):
        """Enhanced verification with more specific checks"""
        for node_type in self.nodes:
            if node_type == NodeType.FN.name:
                continue

            for node in self.nodes[node_type]:
                if random.random() < 0.05:  # 5% verification rate per epoch
                    # Check latency requirements
                    if node.performance_metrics['latency'] > self.node_requirements[NodeType[node_type]].target_ttfb_ms:
                        self.slash_node(node, 'excess_latency')
                    
                    # Check availability
                    elif node.performance_metrics['uptime'] < self.node_requirements[NodeType[node_type]].min_availability:
                        self.slash_node(node, 'unavailability')
                    
                    # Check for log fraud (rare but severe)
                    elif random.random() < 0.01:
                        self.slash_node(node, 'log_fraud')
                    
                    # Check work metrics consistency
                    elif node.work_metrics.total_work_units > 0 and random.random() < 0.02:
                        self.slash_node(node, 'incorrect_data')

    def slash_node(self, node: Node, reason: str):
        """Slash node with offense-specific penalties and distribute to treasury/fishermen"""
        # Define offense-specific penalties
        slash_percentages = {
            'log_fraud': 0.5,         # 50% - Severe: Intentional manipulation
            'unavailability': 0.2,     # 20% - Medium: Service disruption
            'incorrect_data': 0.4,     # 40% - High: Data integrity
            'failed_verification': 0.2, # 20% - Medium: Performance
            'excess_latency': 0.1      # 10% - Low: Performance
        }
        
        # Calculate penalty based on offense and work capacity
        slash_percent = slash_percentages.get(reason, 0.3)
        work_factor = np.log1p(node.work_metrics.total_work_units) / 10  # Scale with work
        
        # Increase penalty for nodes with more work responsibility
        adjusted_slash = slash_percent * (1 + work_factor)
        slash_amount = node.stake * adjusted_slash
        
        # Apply the slash
        node.stake -= slash_amount
        node.slashed = True
        
        # Distribute slashed funds
        treasury_share = 0.7  # 70% to treasury
        fishermen_share = 0.3  # 30% to fishermen
        
        self.treasury_balance += slash_amount * treasury_share
        
        # Distribute to eligible fishermen
        eligible_fishermen = [fn for fn in self.nodes[NodeType.FN.name] 
                            if fn.reputation > 0.9]
        if eligible_fishermen:
            fisherman_reward = (slash_amount * fishermen_share) / len(eligible_fishermen)
            for fn in eligible_fishermen:
                fn.rewards += fisherman_reward

    def get_type_allocation(self, node_type: str) -> float:
        allocations = {
            NodeType.OSN.name: 0.4,
            NodeType.RAN.name: 0.3,
            NodeType.IN.name: 0.2,
            NodeType.FN.name: 0.1
        }
        return allocations.get(node_type, 0.0)

    def update_token_economics(self):
        self.base_inflation_rate *= 0.999  # Slower reduction

        total_rewards = sum(node.rewards 
                          for node_list in self.nodes.values() 
                          for node in node_list)
        self.circulating_supply += total_rewards

        burn_rate = 0.2  # Increased from 0.1 to 0.2 (20% of fees)
        fees_collected = self.calculate_network_fees()
        tokens_to_burn = fees_collected * burn_rate * self.calculate_network_utilization()
        self.burnt_tokens += tokens_to_burn
        self.circulating_supply -= tokens_to_burn

    def calculate_network_fees(self) -> float:
        base_fee = 1000  # Increased base fee
        utilization = self.calculate_network_utilization()
        utilization_factor = np.exp(2 * utilization) - 1
        return base_fee * (1 + utilization_factor)

    def calculate_network_utilization(self) -> float:
        total_nodes = sum(len(nodes) for nodes in self.nodes.values())
        base_utilization = sum(1 for node_list in self.nodes.values() 
                             for node in node_list 
                             if node.performance_metrics['uptime'] > 0.8) / max(1, total_nodes)
        fluctuation = random.uniform(-0.1, 0.1)
        return min(1.0, max(0.0, base_utilization + fluctuation))

    def simulate_epoch(self):
        self.current_epoch += 1

        for node_type in self.nodes:
            for node in self.nodes[node_type]:
                success_rate = random.uniform(0.9, 1.0)
                latency = random.uniform(10, 200)  # ms
                node.update_performance(success_rate, latency)
                node.update_work_metrics(3600)  # Update work metrics for the epoch

        self.distribute_rewards()

        self.verify_nodes()

        self.update_token_economics()

        logger.info(f"Completed epoch {self.current_epoch}")

@dataclass
class NetworkGrowthParameters:
    target_capacity_tbps: float = 100.0  # Target network capacity in Tbps
    target_storage_eb: float = 1.0       # Target storage in Exabytes
    target_utilization: float = 0.8      # Target utilization rate
    years: int = 10                      # Simulation duration in years
    node_capacity_gbps: float = 1.0      # Single node capacity in Gbps
    node_storage_tb: float = 10.0        # Single node storage in TB

@dataclass
class EconomicParameters:
    base_token_price_usd: float = 1.0    # Starting token price
    inflation_rate: float = 0.10         # Annual inflation rate
    customer_growth_rate: float = 0.5    # Annual customer growth rate
    market_cycle_period: float = 4.0     # Years per market cycle
    economic_cycles: bool = True         # Whether to simulate economic cycles

class LongTermSimulation:
    def __init__(self, network_params: NetworkGrowthParameters, economic_params: EconomicParameters):
        self.network_params = network_params
        self.economic_params = economic_params
        self.system = StorachaSystem()
        self.metrics_history = {
            'epoch': [],
            'year': [],
            'network_capacity_tbps': [],
            'storage_capacity_eb': [],
            'utilization_rate': [],
            'token_price_usd': [],
            'total_nodes': [],
            'tokens_staked': [],
            'tokens_circulating': [],
            'tokens_issued': [],
            'customer_revenue': [],
            'foundation_fees': [],
            'node_profitability': [],
            'min_stake_per_node': [],
            'customer_price_per_gb': []
        }

    def calculate_required_nodes(self, current_year: float) -> dict:
        """Calculate required nodes based on target capacity and growth curve"""
        # Use sigmoid growth curve to model network expansion
        growth_factor = 1 / (1 + np.exp(-2 * (current_year - 5)))
        target_capacity = self.network_params.target_capacity_tbps * growth_factor
        target_storage = self.network_params.target_storage_eb * growth_factor

        # Calculate required nodes
        required_osn = int(np.ceil((target_storage * 1e6) / self.network_params.node_storage_tb))
        required_ran = int(np.ceil((target_capacity * 1e3) / self.network_params.node_capacity_gbps))
        required_in = max(20, int(np.ceil(np.sqrt(required_osn + required_ran))))
        required_fn = max(10, int(np.ceil(np.log10(required_osn + required_ran))))

        return {
            NodeType.OSN: required_osn,
            NodeType.RAN: required_ran,
            NodeType.IN: required_in,
            NodeType.FN: required_fn
        }

    def calculate_token_price(self, current_year: float) -> float:
        """Calculate token price with market cycles"""
        if not self.economic_params.economic_cycles:
            return self.economic_params.base_token_price_usd
        
        # Model market cycles using sine wave
        cycle_phase = 2 * np.pi * current_year / self.economic_params.market_cycle_period
        cycle_factor = 1 + 0.5 * np.sin(cycle_phase)
        
        # Add long-term growth trend
        growth_trend = 1 + 0.15 * np.log1p(current_year)
        
        return self.economic_params.base_token_price_usd * cycle_factor * growth_trend

    def run_simulation(self):
        """Run 10-year simulation"""
        epochs_per_year = 8760  # Hourly epochs for a year
        total_epochs = self.network_params.years * epochs_per_year

        for epoch in range(total_epochs):
            current_year = epoch / epochs_per_year
            
            # Update network size based on growth targets
            required_nodes = self.calculate_required_nodes(current_year)
            self._adjust_network_size(required_nodes)
            
            # Update economic parameters
            token_price = self.calculate_token_price(current_year)
            self._update_metrics(epoch, current_year, token_price)
            
            # Run system epoch
            self.system.simulate_epoch()
            
            # Log progress every month
            if epoch % (epochs_per_year // 12) == 0:
                logger.info(f"Simulating Year {current_year:.1f}")

        return self.metrics_history

    def _adjust_network_size(self, required_nodes: dict):
        """Adjust network size to match growth targets"""
        for node_type, required_count in required_nodes.items():
            current_count = len(self.system.nodes[node_type.name])
            
            if current_count < required_count:
                # Add nodes
                for _ in range(required_count - current_count):
                    min_stake = self.system.get_min_stake(node_type)
                    self.system.add_node(node_type, stake=min_stake * 1.5)
            # Note: We don't remove nodes if we have too many

    def _update_metrics(self, epoch: int, year: float, token_price: float):
        """Update simulation metrics"""
        total_nodes = sum(len(nodes) for nodes in self.system.nodes.values())
        total_staked = sum(node.stake for nodes in self.system.nodes.values() for node in nodes)
        
        self.metrics_history['epoch'].append(epoch)
        self.metrics_history['year'].append(year)
        self.metrics_history['network_capacity_tbps'].append(
            len(self.system.nodes[NodeType.RAN.name]) * self.network_params.node_capacity_gbps / 1000)
        self.metrics_history['storage_capacity_eb'].append(
            len(self.system.nodes[NodeType.OSN.name]) * self.network_params.node_storage_tb / 1e6)
        self.metrics_history['utilization_rate'].append(self.system.calculate_network_utilization())
        self.metrics_history['token_price_usd'].append(token_price)
        self.metrics_history['total_nodes'].append(total_nodes)
        self.metrics_history['tokens_staked'].append(total_staked)
        self.metrics_history['tokens_circulating'].append(self.system.circulating_supply)
        self.metrics_history['tokens_issued'].append(
            self.system.circulating_supply + self.system.burnt_tokens)
        self.metrics_history['customer_revenue'].append(
            sum(self.system.calculate_network_fees() for _ in range(24)))  # Daily fees
        self.metrics_history['foundation_fees'].append(self.system.treasury_balance)
        
        # Calculate average node profitability
        avg_rewards = sum(node.rewards 
                         for nodes in self.system.nodes.values() 
                         for node in nodes) / max(1, total_nodes)
        self.metrics_history['node_profitability'].append(avg_rewards * token_price)
        
        # Track minimum stake requirements
        self.metrics_history['min_stake_per_node'].append(
            self.system.get_min_stake(NodeType.OSN))
        
        # Track customer pricing
        self.metrics_history['customer_price_per_gb'].append(
            self.system.calculate_session_cost(SessionParameters(
                storage_load_bytes=1e9,  # 1GB
                read_rate_bps=1e6,      # 1Mbps
                write_rate_bps=1e5,     # 100Kbps
                duration_seconds=30*24*3600,  # 30 days
                request_frequency=1.0,
                collateral=1000
            )))

def run_simulation_example():
    # Initialize the system
    system = StorachaSystem()
    
    # Add nodes with specified capacities
    # Targeting 100 Tbps capacity (80% utilization)
    num_osn = 100  # Each with 1Gbps = 100Gbps total
    num_rqn = 50   # Query nodes
    num_in = 20    # Index nodes
    num_fn = 10    # Fisherman nodes
    
    for _ in range(num_osn):
        system.add_node(NodeType.OSN, stake=150000)  # 1.5x min stake
    for _ in range(num_rqn):
        system.add_node(NodeType.RAN, stake=100000)  # ~1.3x min stake
    for _ in range(num_in):
        system.add_node(NodeType.IN, stake=75000)    # 1.5x min stake
    for _ in range(num_fn):
        system.add_node(NodeType.FN, stake=50000)    # 2x min stake
    
    # Create a realistic session (1TB storage, high bandwidth)
    session = SessionParameters(
        storage_load_bytes=1_000_000_000_000,  # 1TB
        read_rate_bps=1_000_000_000,          # 1Gbps read
        write_rate_bps=100_000_000,           # 100Mbps write
        duration_seconds=30 * 24 * 3600,       # 30 days
        request_frequency=1.0,                 # 1 request per second
        collateral=10000                       # 10k tokens collateral
    )
    
    # Simulate for 720 epochs (30 days with hourly epochs)
    metrics_history = {
        'epoch': [],
        'network_utilization': [],
        'circulating_supply': [],
        'burnt_tokens': [],
        'treasury_balance': [],
        'session_cost': [],
        'avg_node_rewards': []
    }
    
    for epoch in range(720):
        # Calculate session cost
        cost = system.calculate_session_cost(session)
        logger.info(f"Epoch {epoch}: Session cost: ${cost:.2f}")
        
        # Run epoch simulation
        system.simulate_epoch()
        
        # Calculate average node rewards
        total_rewards = sum(node.rewards 
                          for node_list in system.nodes.values() 
                          for node in node_list)
        avg_rewards = total_rewards / sum(len(nodes) for nodes in system.nodes.values())
        
        # Store metrics
        metrics_history['epoch'].append(epoch)
        metrics_history['network_utilization'].append(system.calculate_network_utilization())
        metrics_history['circulating_supply'].append(system.circulating_supply)
        metrics_history['burnt_tokens'].append(system.burnt_tokens)
        metrics_history['treasury_balance'].append(system.treasury_balance)
        metrics_history['session_cost'].append(cost)
        metrics_history['avg_node_rewards'].append(avg_rewards)
        
        # Log key metrics every 24 epochs (daily)
        if epoch % 24 == 0:
            logger.info(f"Day {epoch//24} Summary:")
            logger.info(f"Network utilization: {metrics_history['network_utilization'][-1]:.2%}")
            logger.info(f"Circulating supply: {metrics_history['circulating_supply'][-1]:,.0f}")
            logger.info(f"Burnt tokens: {metrics_history['burnt_tokens'][-1]:,.0f}")
            logger.info(f"Treasury balance: {metrics_history['treasury_balance'][-1]:,.0f}")
            logger.info(f"Avg monthly node revenue: ${avg_rewards*30:.2f}")
            logger.info("-" * 50)
    
    return metrics_history

def write_results_to_file(metrics_history, filename=None):
    # Create results directory if it doesn't exist
    results_dir = "Simulation/results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Generate timestamped filename if none provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{results_dir}/simulation_results_{timestamp}.txt"
    else:
        filename = f"{results_dir}/{filename}"

    with open(filename, 'w') as f:
        f.write(f"Storacha Protocol Simulation Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("===================================\n\n")
        
        # Write simulation parameters
        f.write("Simulation Parameters:\n")
        f.write("---------------------\n")
        f.write("Duration: 30 days (720 epochs)\n")
        f.write("Network Size:\n")
        f.write("- 100 Object Storage Nodes (1Gbps each)\n")
        f.write("- 50 Retrieval Query Nodes\n")
        f.write("- 20 Index Nodes\n")
        f.write("- 10 Fisherman Nodes\n")
        f.write("\nSession Parameters:\n")
        f.write("- Storage: 1TB\n")
        f.write("- Read Bandwidth: 1Gbps\n")
        f.write("- Write Bandwidth: 100Mbps\n")
        f.write("- Duration: 30 days\n")
        f.write("\n")
        
        # Write summary statistics
        f.write("Summary Statistics:\n")
        f.write("-----------------\n")
        
        # Network utilization
        avg_util = sum(metrics_history['network_utilization']) / len(metrics_history['network_utilization'])
        max_util = max(metrics_history['network_utilization'])
        min_util = min(metrics_history['network_utilization'])
        f.write(f"Network Utilization:\n")
        f.write(f"- Average: {avg_util:.2%}\n")
        f.write(f"- Maximum: {max_util:.2%}\n")
        f.write(f"- Minimum: {min_util:.2%}\n\n")
        
        # Token economics
        final_supply = metrics_history['circulating_supply'][-1]
        total_burnt = metrics_history['burnt_tokens'][-1]
        final_treasury = metrics_history['treasury_balance'][-1]
        f.write(f"Token Economics:\n")
        f.write(f"- Final Circulating Supply: {final_supply:,.0f}\n")
        f.write(f"- Total Tokens Burnt: {total_burnt:,.0f}\n")
        f.write(f"- Final Treasury Balance: {final_treasury:,.0f}\n\n")
        
        # Session costs
        avg_cost = sum(metrics_history['session_cost']) / len(metrics_history['session_cost'])
        max_cost = max(metrics_history['session_cost'])
        min_cost = min(metrics_history['session_cost'])
        f.write(f"Session Costs:\n")
        f.write(f"- Average: ${avg_cost:.2f}\n")
        f.write(f"- Maximum: ${max_cost:.2f}\n")
        f.write(f"- Minimum: ${min_cost:.2f}\n\n")
        
        # Node rewards
        avg_rewards = sum(metrics_history['avg_node_rewards']) / len(metrics_history['avg_node_rewards'])
        f.write(f"Node Economics:\n")
        f.write(f"- Average Monthly Revenue per Node: ${avg_rewards*30:.2f}\n\n")
        
        # Daily metrics
        f.write("Daily Metrics:\n")
        f.write("-------------\n")
        num_days = len(metrics_history['circulating_supply']) // 24
        for day in range(num_days):
            epoch_start = day * 24
            epoch_end = min((day + 1) * 24, len(metrics_history['circulating_supply']))
            
            if epoch_start >= len(metrics_history['circulating_supply']):
                break
                
            daily_util = sum(metrics_history['network_utilization'][epoch_start:epoch_end]) / (epoch_end - epoch_start)
            daily_cost = sum(metrics_history['session_cost'][epoch_start:epoch_end]) / (epoch_end - epoch_start)
            daily_rewards = sum(metrics_history['avg_node_rewards'][epoch_start:epoch_end]) / (epoch_end - epoch_start)
            
            f.write(f"\nDay {day + 1}:\n")
            f.write(f"- Network Utilization: {daily_util:.2%}\n")
            f.write(f"- Average Session Cost: ${daily_cost:.2f}\n")
            f.write(f"- Average Node Daily Revenue: ${daily_rewards:.2f}\n")
            f.write(f"- Circulating Supply: {metrics_history['circulating_supply'][epoch_start]:,.0f}\n")
            f.write(f"- Burnt Tokens: {metrics_history['burnt_tokens'][epoch_start]:,.0f}\n")
            f.write(f"- Treasury Balance: {metrics_history['treasury_balance'][epoch_start]:,.0f}\n")

def write_long_term_results(metrics_history, scenario_name):
    """Write long-term simulation results to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = "Simulation/results"
    
    # Create results directory if it doesn't exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        
    filename = f"{results_dir}/long_term_{scenario_name}_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Long-term Simulation Results - {scenario_name}\n")
        f.write("=" * 50 + "\n\n")
        
        if isinstance(metrics_history, dict) and all(isinstance(v, dict) for v in metrics_history.values()):
            # Multiple scenarios in the results
            for scenario, metrics in metrics_history.items():
                f.write(f"\nScenario: {scenario}\n")
                f.write("-" * 30 + "\n")
                write_metrics_summary(f, metrics)
        else:
            # Single scenario
            write_metrics_summary(f, metrics_history)
            
def write_metrics_summary(f, metrics):
    """Helper function to write metrics summary."""
    years = len(metrics['year'])
    for i in range(years):
        f.write(f"\nYear {metrics['year'][i]:.1f}:\n")
        f.write(f"  Network Capacity: {metrics['network_capacity_tbps'][i]:.1f} Tbps\n")
        f.write(f"  Storage Capacity: {metrics['storage_capacity_eb'][i]:.1f} EB\n")
        f.write(f"  Utilization Rate: {metrics['utilization_rate'][i]:.1%}\n")
        f.write(f"  Token Price: ${metrics['token_price_usd'][i]:.2f}\n")
        f.write(f"  Total Nodes: {metrics['total_nodes'][i]}\n")
        f.write(f"  Tokens Staked: {metrics['tokens_staked'][i]:,.0f}\n")
        f.write(f"  Customer Revenue: ${metrics['customer_revenue'][i]:,.2f}\n")
        f.write(f"  Node Profitability: {metrics['node_profitability'][i]:.1%}\n")
        f.write(f"  Customer Price/GB: ${metrics['customer_price_per_gb'][i]:.3f}\n")

def run_inflation_simulation():
    """Run inflation scenarios with different parameters."""
    scenarios = [
        # Base case
        (NetworkGrowthParameters(target_capacity_tbps=100.0, target_storage_eb=1.0, target_utilization=0.8),
         EconomicParameters(inflation_rate=0.10, customer_growth_rate=0.5)),
        # High growth
        (NetworkGrowthParameters(target_capacity_tbps=200.0, target_storage_eb=2.0, target_utilization=0.9),
         EconomicParameters(inflation_rate=0.15, customer_growth_rate=0.7)),
        # Conservative
        (NetworkGrowthParameters(target_capacity_tbps=50.0, target_storage_eb=0.5, target_utilization=0.7),
         EconomicParameters(inflation_rate=0.05, customer_growth_rate=0.3))
    ]
    
    results = []
    for network_params, economic_params in scenarios:
        sim = LongTermSimulation(network_params, economic_params)
        results.append(sim.run_simulation())
    
    return {
        'base_case': results[0],
        'high_growth': results[1],
        'conservative': results[2]
    }

def run_network_growth_simulation():
    """Simulate network growth with different capacity and utilization targets."""
    network_params = NetworkGrowthParameters(
        target_capacity_tbps=150.0,
        target_storage_eb=1.5,
        target_utilization=0.85,
        node_capacity_gbps=2.0,  # Higher capacity nodes
        node_storage_tb=20.0     # Larger storage nodes
    )
    economic_params = EconomicParameters(
        base_token_price_usd=1.0,
        inflation_rate=0.08,     # Lower inflation
        customer_growth_rate=0.6  # Higher customer growth
    )
    
    sim = LongTermSimulation(network_params, economic_params)
    return sim.run_simulation()

def run_profitability_simulation():
    """Simulate node profitability under different token price scenarios."""
    scenarios = []
    base_network = NetworkGrowthParameters(
        target_capacity_tbps=100.0,
        target_storage_eb=1.0,
        target_utilization=0.8
    )
    
    # Test different token prices: $0.1, $0.5, $1.0, $2.0, $5.0
    for price in [0.1, 0.5, 1.0, 2.0, 5.0]:
        economic_params = EconomicParameters(
            base_token_price_usd=price,
            inflation_rate=0.10,
            customer_growth_rate=0.5,
            market_cycle_period=4.0  # 4-year market cycles
        )
        sim = LongTermSimulation(base_network, economic_params)
        scenarios.append((f"price_{price}", sim.run_simulation()))
    
    return dict(scenarios)

def run_customer_revenue_simulation():
    """Simulate transition from token issuance to customer revenue."""
    network_params = NetworkGrowthParameters(
        target_capacity_tbps=120.0,
        target_storage_eb=1.2,
        target_utilization=0.85
    )
    economic_params = EconomicParameters(
        base_token_price_usd=1.0,
        inflation_rate=0.08,      # Lower inflation rate
        customer_growth_rate=0.8  # Higher customer growth rate
    )
    
    sim = LongTermSimulation(network_params, economic_params)
    return sim.run_simulation()

def run_foundation_accumulation_simulation():
    """Simulate foundation token accumulation from network fees."""
    network_params = NetworkGrowthParameters(
        target_capacity_tbps=100.0,
        target_storage_eb=1.0,
        target_utilization=0.9  # High utilization for more fees
    )
    economic_params = EconomicParameters(
        base_token_price_usd=1.5,  # Higher token price
        inflation_rate=0.10,
        customer_growth_rate=0.6
    )
    
    sim = LongTermSimulation(network_params, economic_params)
    return sim.run_simulation()

if __name__ == "__main__":
    # Run short-term simulation for testing
    metrics = run_simulation_example()
    write_results_to_file(metrics)
    
    # Run long-term simulations
    logger.info("Running inflation scenarios...")
    inflation_results = run_inflation_simulation()
    write_long_term_results(inflation_results, "inflation")
    
    logger.info("Running network growth simulation...")
    growth_results = run_network_growth_simulation()
    write_long_term_results(growth_results, "network_growth")
    
    logger.info("Running profitability simulation...")
    profitability_results = run_profitability_simulation()
    write_long_term_results(profitability_results, "profitability")
    
    logger.info("Running customer revenue simulation...")
    revenue_results = run_customer_revenue_simulation()
    write_long_term_results(revenue_results, "customer_revenue")
    
    logger.info("Running foundation accumulation simulation...")
    foundation_results = run_foundation_accumulation_simulation()
    write_long_term_results(foundation_results, "foundation")
    
    logger.info("All simulations completed. Results written to Simulation/results/")