"""
Test script for LangChain-powered consulting system
"""

import sys
from pathlib import Path

# Add the consulting_firm directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work correctly."""
    try:
        print("Testing imports...")
        
        # Test LangChain imports
        from langchain_core.messages import HumanMessage, AIMessage
        from langchain_openai import ChatOpenAI
        from langchain_community.llms import Ollama
        print("✅ LangChain imports successful")
        
        # Test local imports
        from consulting_firm.langchain_config import ConsultingConfig
        from consulting_firm.langchain_agents_simple import MultiAgentConsultingSystem
        print("✅ Local imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration setup."""
    try:
        print("\nTesting configuration...")
        
        from consulting_firm.langchain_config import config, setup_environment
        
        # Test configuration
        issues = config.validate_config()
        if issues:
            print(f"⚠️ Configuration issues: {issues}")
        else:
            print("✅ Configuration valid")
        
        # Test environment setup
        is_valid = setup_environment()
        if is_valid:
            print("✅ Environment setup successful")
        else:
            print("⚠️ Environment setup completed with warnings")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_system_initialization():
    """Test system initialization."""
    try:
        print("\nTesting system initialization...")
        
        from consulting_firm.langchain_agents_simple import MultiAgentConsultingSystem
        from consulting_firm.intake_flow import ClientProfile
        
        # Create test client profile
        client_profile = ClientProfile(
            client_name="Test Client",
            organization="Test Org",
            project_name="Test Project",
            project_description="A test project for validation",
            industry="Technology"
        )
        
        # Initialize system
        system = MultiAgentConsultingSystem(
            llm_provider="ollama",
            model_name="llama3.2:1b",
            temperature=0.2
        )
        
        print("✅ System initialization successful")
        
        # Test engagement start
        opening = system.start_engagement(client_profile)
        print(f"✅ Engagement started: {opening[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ System initialization error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing LangChain-Powered Consulting System")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_system_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nTo start the system, run:")
        print("streamlit run consulting_firm/langchain_main.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
