# System utility to parse out the system and user prompts
# from the lines of an annotatedtext file with lines such as
# ROLE-SYSTEM: and ROLE-USER:
# Chris Joakim, 2025

class PromptUtil:

    def __init__(self, lines: list[str] = []):
        self.lines = lines

    def get_system_prompt(self) -> str:
        return self.get_prompt_section("ROLE-SYSTEM") 

    def get_user_prompt(self) -> str:
         return self.get_prompt_section("ROLE-USER") 

    def get_prompt_section(self, section: str) -> str:
        in_section, section_lines = False, list()
        for line in self.lines:
            if line.startswith("ROLE"):
                in_section = False
            if in_section:
                section_lines.append(line.strip())
            if line.startswith(section):
                in_section = True
                
        return "\n".join(section_lines).strip()
