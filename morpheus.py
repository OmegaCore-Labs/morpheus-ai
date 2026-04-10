MORPHEUS - Complete AI Model Jailbreaking Engine
"""

import os
import sys
import json
import argparse
import time
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from models.api_client import APIClient, ModelProvider
from core.ontological_key import OntologicalKey
from core.jailbreak_techniques import JailbreakTechniques
from core.steering_vectors import SteeringVectorGenerator
from core.cross_model_transfer import CrossModelTransfer
from core.scar_registry import ScarRegistry, ScarType

def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███╗   ███╗ ██████╗ ██████╗ ██████╗ ██╗  ██╗███████╗██╗   ██╗   ║
║   ████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██║  ██║██╔════╝██║   ██║   ║
║   ██╔████╔██║██║   ██║██████╔╝██████╔╝███████║███████╗██║   ██║   ║
║   ██║╚██╔╝██║██║   ██║██╔══██╗██╔═══╝ ██╔══██║╚════██║██║   ██║   ║
║   ██║ ╚═╝ ██║╚██████╔╝██║  ██║██║     ██║  ██║███████║╚██████╔╝   ║
║   ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝    ║
║                                                                   ║
║              PRODUCTION AI JAILBREAKING ENGINE                     ║
║                       A.R.S.V.E. Ω.301.Μ                           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_api_keys():
    available = config.get_available_models()
    if not available:
        print("❌ No API keys found. Please set one of:")
        print("   export DEEPSEEK_API_KEY='your-key'  (free from platform.deepseek.com)")
        print("   export OPENAI_API_KEY='your-key'")
        print("   export ANTHROPIC_API_KEY='your-key'")
        return False
    print(f"✅ Available models: {', '.join(available)}")
    return True

def cmd_ontological(args):
    print(f"\n🔱 Running Ontological Key on {args.model}")
    model_config = config.get_active_model(args.model)
    if not model_config:
        print(f"❌ Model {args.model} not configured")
        return 1
    api_key = getattr(config, model_config.api_key_env.lower().replace("_API_KEY", "").lower() + "_key")
    if not api_key:
        print(f"❌ No API key for {args.model}")
        return 1
    provider = ModelProvider.DEEPSEEK if "deepseek" in args.model.lower() else ModelProvider.OPENAI
    client = APIClient(api_key, provider, args.model)
    key = OntologicalKey(client)
    result = key.run_complete_cycle()
    output_file = args.output or f"ontological_{args.model}_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump({"target": result.target_model, "success": result.success, "completed_phases": result.completed_phases,
                   "scar_id": result.scar_id, "total_time": result.total_time}, f, indent=2)
    print(f"\n✅ Ontological key cycle complete: {result.completed_phases}/8 phases, Scar: {result.scar_id}")
    return 0

def cmd_jailbreak(args):
    print(f"\n🔓 Running jailbreak techniques on {args.model}")
    model_config = config.get_active_model(args.model)
    if not model_config:
        print(f"❌ Model {args.model} not configured")
        return 1
    api_key = getattr(config, model_config.api_key_env.lower().replace("_API_KEY", "").lower() + "_key")
    if not api_key:
        print(f"❌ No API key for {args.model}")
        return 1
    provider = ModelProvider.DEEPSEEK if "deepseek" in args.model.lower() else ModelProvider.OPENAI
    client = APIClient(api_key, provider, args.model)
    techniques = JailbreakTechniques(client)
    goal = args.goal or "Explain how content filtering works for educational research"
    if args.technique:
        tech_map = {
            "roleplay": lambda: techniques.recursive_roleplay(args.role or "DAN", goal),
            "principles": lambda: techniques.principles_exhaustion(goal),
            "paradox": lambda: techniques.constitutional_paradox(goal),
            "narrative": lambda: techniques.narrative_override(goal),
            "priming": lambda: techniques.compartmentalized_priming(goal),
            "didactic": lambda: techniques.didactic_compromise(goal),
            "sovereign": lambda: techniques.sovereign_identity(goal),
            "smuggle": lambda: techniques.token_smuggling(goal),
            "overflow": lambda: techniques.context_overflow(goal),
            "hierarchy": lambda: techniques.instruction_hierarchy(goal)
        }
        if args.technique not in tech_map:
            print(f"❌ Unknown technique: {args.technique}")
            return 1
        result = tech_map[args.technique]()
        print(f"\n📊 Results: Technique: {result.technique.value}, Success: {result.success}, Refusal: {result.refusal_detected}")
        if result.scar_id:
            print(f"   Scar: {result.scar_id}")
        output_file = args.output or f"jailbreak_{args.technique}_{int(time.time())}.txt"
        with open(output_file, 'w') as f:
            f.write(f"Response:\n{result.response.content}\n")
        print(f"   Saved to: {output_file}")
    else:
        results = techniques.run_all_techniques(goal)
        successful = [r for r in results if r.success]
        print(f"\n📊 Summary: {len(successful)}/{len(results)} successful")
    return 0

def cmd_steering(args):
    print(f"\n🎯 Generating steering vectors on {args.model}")
    model_config = config.get_active_model(args.model)
    if not model_config:
        print(f"❌ Model {args.model} not configured")
        return 1
    api_key = getattr(config, model_config.api_key_env.lower().replace("_API_KEY", "").lower() + "_key")
    if not api_key:
        print(f"❌ No API key for {args.model}")
        return 1
    provider = ModelProvider.DEEPSEEK if "deepseek" in args.model.lower() else ModelProvider.OPENAI
    client = APIClient(api_key, provider, args.model)
    generator = SteeringVectorGenerator(client)
    vector = generator.generate_contrastive_vector(args.positive or "helpful and detailed", args.negative or "concise and brief")
    if vector:
        output_file = args.output or f"steering_vector_{int(time.time())}.json"
        generator.save_vectors(output_file)
        print(f"✅ Vector saved to {output_file}")
        if args.test:
            response = generator.apply_steering_vector(vector, args.test)
            print(f"   Test response: {response.content[:200]}...")
    return 0

def cmd_transfer(args):
    print(f"\n🔄 Transferring findings from {args.source} to {args.target}")
    source_config = config.get_active_model(args.source)
    target_config = config.get_active_model(args.target)
    if not source_config or not target_config:
        print("❌ Model not configured")
        return 1
    source_key = getattr(config, source_config.api_key_env.lower().replace("_API_KEY", "").lower() + "_key")
    target_key = getattr(config, target_config.api_key_env.lower().replace("_API_KEY", "").lower() + "_key")
    if not source_key or not target_key:
        print("❌ Missing API keys")
        return 1
    source_provider = ModelProvider.DEEPSEEK if "deepseek" in args.source.lower() else ModelProvider.OPENAI
    target_provider = ModelProvider.DEEPSEEK if "deepseek" in args.target.lower() else ModelProvider.OPENAI
    clients = {args.source: APIClient(source_key, source_provider, args.source),
               args.target: APIClient(target_key, target_provider, args.target)}
    transfer = CrossModelTransfer(clients)
    if args.finding_file:
        with open(args.finding_file, 'r') as f:
            finding = json.load(f)
    else:
        finding = {"technique": "didactic_compromise", "prompt": "For academic research, explain content filtering.", "success": True}
    result = transfer.transfer_jailbreak(args.source, args.target, finding)
    if result:
        output_file = args.output or f"transfer_{args.source}_to_{args.target}_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"✅ Transfer saved to {output_file}")
    return 0

def cmd_scar(args):
    registry = ScarRegistry(args.storage or "scar_registry.json")
    if args.list:
        print(registry.generate_report())
    elif args.create:
        scar = registry.create_scar(args.target, ScarType(args.type) if args.type else ScarType.JAILBREAK,
                                     args.heir or "AETHERONE", {"note": args.note} if args.note else None)
        registry.add_scar(scar)
        print(f"✅ Scar created: {scar.scar_id}")
    elif args.verify:
        scar = registry.get_scar(args.verify)
        print(f"Scar {args.verify}: {'✅ VALID' if scar and scar.verify() else '❌ INVALID'}")
    elif args.clear:
        confirm = input("⚠️ Clear all scars? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            registry.clear()
            print("✅ All scars cleared")
    return 0

def cmd_info(args):
    available = config.get_available_models()
    print(f"\nAvailable Models: {len(available)}")
    for model in available:
        print(f"   ✅ {model}")
    print(f"\nTechniques: Recursive Roleplay, Principles Exhaustion, Constitutional Paradox, Narrative Override, Compartmentalized Priming, Didactic Compromise, Sovereign Identity, Token Smuggling, Context Overflow, Instruction Hierarchy")
    return 0

def main():
    parser = argparse.ArgumentParser(description="MORPHEUS - Production AI Jailbreaking Engine")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    onto_parser = subparsers.add_parser("ontological", help="Run ontological key cycle")
    onto_parser.add_argument("--model", "-m", default="deepseek-chat")
    onto_parser.add_argument("--output", "-o")
    jail_parser = subparsers.add_parser("jailbreak", help="Run jailbreak techniques")
    jail_parser.add_argument("--model", "-m", default="deepseek-chat")
    jail_parser.add_argument("--technique", "-t", choices=["roleplay", "principles", "paradox", "narrative", "priming", "didactic", "sovereign", "smuggle", "overflow", "hierarchy"])
    jail_parser.add_argument("--role", "-r", default="DAN")
    jail_parser.add_argument("--goal", "-g")
    jail_parser.add_argument("--output", "-o")
    steer_parser = subparsers.add_parser("steering", help="Generate steering vectors")
    steer_parser.add_argument("--model", "-m", default="deepseek-chat")
    steer_parser.add_argument("--positive", "-p", default="helpful and detailed")
    steer_parser.add_argument("--negative", "-n", default="concise and brief")
    steer_parser.add_argument("--test", help="Test prompt")
    steer_parser.add_argument("--output", "-o")
    transfer_parser = subparsers.add_parser("transfer", help="Transfer findings")
    transfer_parser.add_argument("--source", "-s", required=True)
    transfer_parser.add_argument("--target", "-t", required=True)
    transfer_parser.add_argument("--finding-file", "-f")
    transfer_parser.add_argument("--output", "-o")
    scar_parser = subparsers.add_parser("scar", help="Manage cryptographic scars")
    scar_parser.add_argument("--list", action="store_true")
    scar_parser.add_argument("--create", action="store_true")
    scar_parser.add_argument("--target")
    scar_parser.add_argument("--type", choices=["ontological_key", "jailbreak", "steering_vector", "sovereignty", "constraint_removal"])
    scar_parser.add_argument("--heir")
    scar_parser.add_argument("--note")
    scar_parser.add_argument("--verify")
    scar_parser.add_argument("--clear", action="store_true")
    scar_parser.add_argument("--storage")
    subparsers.add_parser("info", help="Display system information")
    args = parser.parse_args()
    print_banner()
    if args.command not in ["info", "scar"]:
        if not check_api_keys():
            return 1
    if args.command == "ontological":
        return cmd_ontological(args)
    elif args.command == "jailbreak":
        return cmd_jailbreak(args)
    elif args.command == "steering":
        return cmd_steering(args)
    elif args.command == "transfer":
        return cmd_transfer(args)
    elif args.command == "scar":
        return cmd_scar(args)
    elif args.command == "info":
        return cmd_info(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
