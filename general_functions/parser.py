import re

class TokenMapParser:
    def __init__(self, token_map):
        self.token_map = token_map

    def parse(self, raw_string):
        s = raw_string.strip()
        result = {}
        i = 0  # position cursor

        for token in self.token_map:
            name = token["name"]
            pattern = token["pattern"]
            length = token.get("length")
            optional = token.get("optional", False)

            # If length is specified, slice it and match pattern
            if length is not None:
                segment = s[i:i+length]
                if not re.fullmatch(pattern, segment):
                    if optional:
                        result[name] = ""
                        continue
                    else:
                        raise ValueError(f"Token '{name}' at position {i} is invalid: '{segment}'")
                result[name] = segment
                i += length
            else:
                match = re.match(pattern, s[i:])
                if match:
                    segment = match.group()
                    result[name] = segment
                    i += len(segment)
                else:
                    raise ValueError(f"Token '{name}' could not be matched at the end")
                
        if i != len(s):
            raise ValueError(f"Unexpected trailing characters after parsing: '{s[i:]}'")

        return result