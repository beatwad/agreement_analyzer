from typing import Dict, List

import textwrap
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta
import random
import time
import httpx

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from google.genai import types

import prompts


def pause(low: int = 1, high: int = 2) -> None:
    """
    Pause for a random amount of time between low and high seconds.
    Used to simulate user behavior.
    """
    pause = round(random.uniform(low, high), 1)
    time.sleep(pause)


class AIModel(ABC):
    @abstractmethod
    def invoke(self, prompt: str) -> str:
        pass


class GeminiModel(AIModel):
    """Get access to Gemini model"""

    def __init__(self, api_key: str, llm_model: str, llm_proxy: str, temperature: float) -> None:
        from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory

        self.google_api_key = api_key

        # Configure HTTP options with proxy if provided
        model_kwargs = {
            "model": llm_model,
            "google_api_key": self.google_api_key,
            "temperature": temperature,
            "safety_settings": {
                HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
                # HarmCategory.HARM_CATEGORY_DEROGATORY: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_TOXICITY: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_VIOLENCE: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUAL: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_MEDICAL: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        }

        if llm_proxy:
            http_options = types.HttpOptions(
                client_args={"proxy": llm_proxy}, async_client_args={"proxy": llm_proxy}
            )
            model_kwargs["http_options"] = http_options

        self.model = ChatGoogleGenerativeAI(**model_kwargs)

    def invoke(self, prompt: ChatPromptTemplate) -> BaseMessage:
        prompt_messages = [SystemMessage(content=prompts.system_role)] + prompt.messages
        # randomly select one proxy after another until LLM request succeeds
        response = self.model.invoke(prompt_messages)
        return response


class OpenAIModel(AIModel):
    """Get access to OpenAI model"""

    def __init__(
        self, api_key: str, llm_model: str, llm_proxy: str = None, temperature: float = 0.4
    ) -> None:
        from langchain_openai import ChatOpenAI

        if llm_proxy:
            http_client = httpx.Client(proxy=llm_proxy)
        else:
            http_client = None
        self.llm_proxy = llm_proxy
        self.model_name = llm_model
        self.openai_api_key = api_key
        self.model = ChatOpenAI(
            model_name=self.model_name,
            openai_api_key=self.openai_api_key,
            http_client=http_client,
            temperature=1 if "o1" in self.model_name or "gpt-5" in self.model_name else temperature,
            presence_penalty=0,
            frequency_penalty=0,
            timeout=60,
            reasoning_effort="minimal",
        )

    def invoke(self, prompt: ChatPromptTemplate) -> BaseMessage:
        prompt_messages = [SystemMessage(content=prompts.system_role)] + prompt.messages
        response = self.model.invoke(prompt_messages)
        return response


class ClaudeModel(AIModel):
    """Get access to Claude model"""

    def __init__(self, api_key: str, llm_model: str, temperature: float) -> None:
        from langchain_anthropic import ChatAnthropic

        self.model = ChatAnthropic(model=llm_model, api_key=api_key, temperature=temperature)

    def invoke(self, prompt: str) -> BaseMessage:
        response = self.model.invoke(prompt)
        return response


class OllamaModel(AIModel):
    """Get access to Ollama model"""

    def __init__(self, llm_model: str, llm_api_url: str) -> None:
        from langchain_ollama import ChatOllama

        if len(llm_api_url) > 0:
            self.model = ChatOllama(model=llm_model, base_url=llm_api_url)
        else:
            self.model = ChatOllama(model=llm_model)

    def invoke(self, prompt: str) -> BaseMessage:
        response = self.model.invoke(prompt)
        return response


class AIAdapter:
    """Class for accessing LLM models from different companies via API"""

    def __init__(
        self,
        api_key: str,
        llm_proxy: str,
        llm_provider: str,
        llm_model: str,
        temperature: float,
        free_tier: bool,
        free_tier_rpm_limit: int,
        llm_api_url: str = None,
    ):
        self.model_provider = llm_provider
        self.llm_model = llm_model
        self.temperature = temperature
        self.free_tier = free_tier
        self.free_tier_rpm_limit = free_tier_rpm_limit
        self.free_tier_request_queue = deque(maxlen=self.free_tier_rpm_limit)
        self.model = self._create_model(api_key, llm_proxy, llm_api_url)

    def _create_model(self, api_key: str, llm_proxy: str, llm_api_url: str) -> AIModel:
        if self.model_provider == "Gemini":
            return GeminiModel(api_key, self.llm_model, llm_proxy, self.temperature)
        elif self.model_provider == "OpenAI":
            return OpenAIModel(api_key, self.llm_model, llm_proxy, self.temperature)
        elif self.model_provider == "Claude":
            return ClaudeModel(api_key, self.llm_model, self.temperature)
        elif self.model_provider == "Ollama":
            return OllamaModel(self.llm_model, llm_api_url)
        else:
            # Fallback or error for unknown provider, trying lower case match if needed
            provider_lower = self.model_provider.lower()
            if provider_lower == "gemini":
                return GeminiModel(api_key, self.llm_model, llm_proxy, self.temperature)
            elif provider_lower == "openai":
                return OpenAIModel(api_key, self.llm_model, llm_proxy, self.temperature)
            elif provider_lower == "claude":
                return ClaudeModel(api_key, self.llm_model, self.temperature)
            elif provider_lower == "ollama":
                return OllamaModel(self.llm_model, llm_api_url)

            raise ValueError(f"Unsupported model type: {self.model_provider}")

    def invoke(self, prompt: str) -> str:
        if self.free_tier:
            if len(self.free_tier_request_queue) >= self.free_tier_rpm_limit:
                first_request_timestamp = self.free_tier_request_queue.popleft()
                time_delta = datetime.now() - first_request_timestamp
                if time_delta < timedelta(seconds=60):
                    pause(60 - time_delta.total_seconds(), 60 - time_delta.total_seconds() + 1)
            self.free_tier_request_queue.append(datetime.now())
        return self.model.invoke(prompt)


class LoggerChatModel:
    """
    Class for interacting with language model (LLM) and logging all operations.
    This class processes requests to the language model, parses and logs responses, and handles
    possible errors such as rate limit exceeded or network errors.
    """

    def __init__(self, llm: GeminiModel):
        self.llm = llm

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        """
        Execute LLM call, process response and log the entire process.
        """
        reply = self.llm.invoke(messages)
        return reply


class GPTAnswerer:
    """
    Class for processing resume questions and generating answers using LLM.
    The class includes methods for processing and determining resume sections such as
    personal information, work experience, etc., based on provided questions.
    Designed for automating resume question responses,
    as well as writing cover letters.
    """

    def __init__(
        self,
        api_key: str,
        llm_proxy: str,
        llm_provider: str,
        llm_model: str,
        temperature: float,
        free_tier: bool,
        free_tier_rpm_limit: int,
    ):
        self.job = None
        self.ai_adapter = AIAdapter(
            api_key, llm_proxy, llm_provider, llm_model, temperature, free_tier, free_tier_rpm_limit
        )
        self.llm_cheap = LoggerChatModel(self.ai_adapter)
        self.chains = {
            "analyze_agreement": self._create_chain(prompts.analyze_agreement_prompt),
        }

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        """Transform template string for use in prompts."""
        return textwrap.dedent(template)

    def _create_chain(self, template: str) -> ChatPromptTemplate:
        """Create a chain for a specific resume section."""
        template = self._preprocess_template_string(template)
        prompt = ChatPromptTemplate.from_template(template)
        return prompt | self.llm_cheap | StrOutputParser()

    def analyze_agreement(self, text: str) -> str:
        """
        Analyze agreement
        """
        chain = self.chains["analyze_agreement"]
        output = chain.invoke({"text": text})
        return output
