from ast_ import *
from lexer import TokenType
NOTES = [TokenType.do,TokenType.re,TokenType.mi,TokenType.fa,TokenType.sol,TokenType.la,TokenType.si, TokenType.KW_R]
END_STATEMENT = [TokenType.NL, TokenType.SEMICOLON, TokenType.EOF]

class ParseState:

    MOVEMENT = "MOVEMENT"
    MACRO = "MACRO"
    
    EXPR = "EXPR"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.stack = []
        self.tracks = []
        self.macros = []
        self.metadata = []
        self.idents = {}
        self.err_list = []
        self.log_list = []

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            return self.tokens[self.pos - 1]
        return self.tokens[-1]  # Return EOF token

    def peek(self, offset):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF token

    def match(self, token_type):
        curr = self.peek(0).type
        if curr == token_type:
            return True
        else :
            return False

    def expect(self, token_type):
        if self.peek(0).type == token_type:
            return self.advance()
        else:
            return None

    def log(self,msg):
        self.log_list.append(msg)


    def parse(self):
        # Create program node (root of AST)
        #update metadata if you want to add for example

        if TokenType.KW_TRACK not in self.tokens:
            self.log("Added global track")
            self.tracks.append(Track("global",[],self.peek(0)))
            pass

        # Skip initial newlines
        self.skip_whitespace()
        
        # Continue parsing until we reach EOF
        while self.peek(0).type != TokenType.EOF:
            self.log(f"new iteration of statement loop at {self.peek(0)}")

            # Handle expected error cases:
            if self.peek(0).type in NOTES:
                self.log(f"Error: note literal as statement")
                self.err_list.append(f"""{SyntaxErr(self.peek(0))}Statements cannot start with a note literal.
|
| Tip: To write notes or expressions over multiple lines use an exression group by enclosing them in []
|
|   Example:
|   X piano: 
|           do re mi
|
|   V piano: [
|           do re mi
|   ]
|
""")
                self.restore_stmt()
                continue


            # Handle metadata
            if self.peek(0).type == TokenType.KW_TITLE:
                self.log("found title")
                self.advance() # consume title token
                self.skip_space()

                if self.expect(TokenType.COLON) is None:
                    self.log(f"expected colon but found {self.peek(0)}")
                    self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected colon after keyword title, got token \"{self.peek(0).value}\" intead\n" )
                    self.restore_stmt()
                else:
                    self.log("found colon in metadata")
                    self.skip_space()
                    name = self.expect(TokenType.STRING)

                    if name is not None:
                        self.log(f"found name for title {name}")
                        self.metadata.append(Metadata(name.value,name))
                    else:
                        self.log(f"title error")
                        self.err_list.append(f"{SyntaxErr(name)}Expected string after title definiton, got token \"{name.value}\" instead\n")
                        self.restore_stmt()


            # Handle macro definition or movement
            elif self.peek(0).type == TokenType.ALPHANUM:
                self.log(f"found alphanum:{self.peek(0)}")
                ident = self.advance()
                self.skip_space()
                # parse macros
                if self.peek(0).type in [TokenType.EQUAL,TokenType.OPEN_PAREN]:
                    self.log("parsing macros")
                    
                    # if it's a macro, it needs to be added to ident list
                    if ident.value in self.idents.keys():
                        self.log(f"adding macro {ident} to ident list")

                        if not isinstance(self.idents[ident.value],Token) :
                            self.log(f"idents already defined error")
                            self.err_list.append(f"{Ident_err(ident)}Identifier {ident.value} is already used here:{self.idents[ident.value]}, redefinitions are not allowed")
                    self.log(f"register ident for macro {ident}")
                    self.idents[ident.value] = ident

                    self.log(f"push macro state")
                    self.stack.append(ParseState.MACRO)
                    self.log(f"call parse macro")
                    macro = self.parse_macro(ident)
                    self.log(f"append macro {macro}")
                    self.macros.append(macro)
                    
                    self.log(f"assign index of macro to the map")
                    self.idents[ident.value] = len(self.macros)

                    self.log(f"pop macro from stack")
                    top = self.stack.pop()
                    if top != ParseState.MACRO:
                        self.log(f"top of stack wasnt macro")
                        self.dump_state()
                        raise ValueError(f"Internal error: Expected Macro state on top of the stack, got {top} intead")

                # parse movements
                elif self.peek(0).type in [TokenType.STRING , TokenType.COLON]:
                    self.log(f"push MOVEMENT to stack")
                    self.stack.append(ParseState.MOVEMENT)
                    self.log(f"call parse movemet")
                    movement = self.parse_movement(ident)
                    self.log("append to the last defined track")
                    self.tracks[-1].movements.append(movement)
                    self.skip_whitespace()
                    self.skip_space()


                    self.log("add the identifier for the movement to the list")
                    m_ident = f"{movement.instrument.value}{movement.tag if movement.tag == "" else movement.tag.value}"
                    if (m_ident not in self.idents.keys()  # if the movement isn't defined already
                        or self.idents[m_ident][0] != len(self.tracks) # or if defined, doesn't belong to the same track
                    ):
                        self.log("added new ident for movement")
                        self.idents[m_ident] = (len(self.tracks), len(self.tracks[-1].movements))
                    else:
                        tag_already_exists = f'''Tag {m_ident} already exits {self.idents[m_ident]}'''
                        instrument_already_used = f'''Instrument {movement.instrument} was already used in this track:{self.idents[m_idents]} 
| Tip: to have the same instrument playing twice in a movement, use a tag to differentiate it:
| x piano : do re mi
|   piano : fa sol la
|
| v piano : do re mi
|   piano "another" : fa sol la
'''
                        self.err_list.append(f"{instrument_already_used if movement.tag == "" else tag_already_exists }")
                        pass

                    self.log("pop from stack movement")
                    top = self.stack.pop()
                    if top != ParseState.MOVEMENT:
                        self.log(f"expected to pop movemnt, got {top} instead")
                        self.dump_state()
                        raise ValueError(f"Compiler error: Expected Movement state on top of the stack, got {top} intead")
                    pass

                else:
                    self.log("192: token error") # there is no standard way to create log messeges, i kinda wing them
                    self.err_list.append(f"{SyntaxErr(self.peek(0))}Unexpected token after alphanum: {self.peek(0)}")
                    self.restore_stmt()

            elif self.peek(0).type == TokenType.KW_TRACK:
                self.log("found track kw")
                source = self.advance()
                name = "main"
                self.skip_space()
                
                if self.match(TokenType.STRING):
                    name = self.advance()
                    self.skip_space()
                    self.log(f"found name for track {name}")

                if self.match(TokenType.COLON):
                    self.log("found colon after track kw")
                    self.advance()
                    self.skip_whitespace()

                else :
                    self.log(f"213: token error")
                    self.err_list.append(f"{SyntaxErr(self.peek(1))} Expected colon or string after \"track\" , got token \"{self.peek(1).value}\" instead")
                    self.restore_to(TokenType.NL)


            elif self.peek(0).type == TokenType.NL:
                self.log("Skip newlines between statements")
                self.advance()
            else:
                self.log("Handle unexpected tokens for start of statements")
                self.err_list.append(
                    f"{SyntaxErr(self.peek(0))}Unexpected token \"{self.peek(0)}\" for begining of new statement \n") + '''
| Tip: The supported types of statements are:
| 1. Metadata statements
|   example: title = "my title"
|
| 2. Track start statements
|   example: track "my track":
|   Note: a track end when either the file ends or another track is defined
|         also, if no track is defined, the entire file is treated as the track
|
| 3. Movements
|   example: piano "melodi": do re mi
|
| 4. Macros
|   example: my_macro = do re mi
|            my_macro_with_arguments (arg1,arg2) = arg1 do re mi arg2
|
'''
                self.restore_stmt()

        self.log(f"finished parsing program")
        return Program(self.metadata,self.macros,self.tracks, self.tokens[self.pos],self.idents,self.err_list)

    def parse_movement(self,instr):
        
        tag = ""
        body = []

        if self.match(TokenType.STRING):
            tag = self.advance()
            self.log(f"found tag {tag} for movement {instr}")
            self.skip_space()

        if self.expect(TokenType.COLON) is None:
            self.log(f"258: token error")
            self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected colon after movement {instr} {self.log_tk()}")

        while self.peek(0).type not in END_STATEMENT:
            self.log("iterating movement body")
            self.skip_space()
            self.log("calling parse expr")
            new_expr = self.parse_expr()
            self.log(f"appending new_expr to body")
            body.append(new_expr)
            self.skip_space()
        self.log("iteration of movemnt stoped")

        return Movement(instr,tag,body)

    def parse_macro(self, name):
        parameters = []
        body = []
        
        if self.peek(0).type == TokenType.OPEN_PAREN:
            self.log("Parse parameters in macro")
            self.advance() # consume open paren token
            self.skip_space()

            while True:
                self.log("iteration of arguments for macro")
                if self.match(TokenType.CLOSE_PAREN):
                    self.log("found close paren while parsing arguments")
                    self.advance()
                    break

                
                elif self.match(TokenType.ALPHANUM):
                    param = self.advance()
                    parameters.append(param) 
                    self.idents[param.value] = param
                    self.log(f"got some parameters that are alphanum:{param}")

                    self.skip_space()

                    # Parse additional parameters separated by commas
                    if self.match(TokenType.COMMA):
                        self.log("found comma, more parameters to parse")
                        self.advance()  # Skip comma
                        self.skip_space()

                        if self.peek(0).type == TokenType.ALPHANUM:
                            self.log(f"next parameter is alphanum, continuing")
                            continue

                        elif self.peek(0).type == TokenType.CLOSE_PAREN:
                            self.log(f"309: token err")
                            self.err_list.append(f"{SyntaxErr(self.peek(0))}Trailing comma in macro definition arguments: \"{self.peek(0).value}\"")
                            self.log("restoer by skipping close paren token")
                            self.advance()
                        else:
                            self.log("314: token err")
                            self.err_list.append(
                                f"{SyntaxErr(self.peek(0))}Expected parameter type, got \"{self.peek(0)}\" instead of an identifier")
                            self.log("restore by skipping that token")
                            self.advance()
                            pass
                        pass
                    
                    elif self.match(TokenType.CLOSE_PAREN):
                        self.log("if no comma, has to be close paren")
                        self.advance()
                        break
                    else:
                        self.log("327: token err")
                        self.err_list.append(f"{SyntaxErr(self.peek(0))}Macro parameter must be fallowed by comma or closed parenthesi, got token \"{self.peek(0).value}\" instead")
                        self.restore_to(TokenType.NL,TokenType.CLOSE_PAREN)
                    pass
                else:
                    self.log("332: token err")
                    self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected identifier in arguments body, got token \"{self.peek(0).value}\" instead")
                pass

        self.log("end of parsing parameters")

        self.skip_space()
            
        if not self.match(TokenType.EQUAL):
            self.log("341: token err")
            self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected equals sign after macro name or arguments",self.log_tk())
            self.restore_stmt()

        self.advance() # skip equal token
        self.skip_space()

        self.log("Parse macro body")

        while self.peek(0).type not in END_STATEMENT:
            self.skip_space()
            self.log("Parse expr in macro body")
            body.append(self.parse_expr())
    


        self.log("End of parsing macro body")
        self.advance()

        return Macro(name, parameters, body) 


    def parse_expr(self):
        self.log("push expr to stack")
        self.stack.append(ParseState.EXPR)
        expression = None

        if False:
            todo("remove this branch later")


# simple expressions

        
        elif self.match(TokenType.V):
            self.log("Parse SetVolume")
            source = self.advance()

            self.skip_space()

            if self.expect(TokenType.EQUAL) is None:
                err_source = self.peek(0)
                self.log("380: token err")
                self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected colon after keyword {source.value}{self.log_tk()}")
                self.restore_to(TokenType.SPACE)
                expression = errExpr(err_source) 

                self.log("pop expr from stack")
                top = self.stack.pop()
                if top != ParseState.EXPR:
                    self.log(f"not expr on top, {top}")
                    self.dump_state()
                    raise ValueError(f"Expected expr on top of the stack, got {top} instead")

                return expression
            
            if self.match(TokenType.NUM):
                expression = SetVolume(int(self.advance().value),source)
            else:
                err_source = self.peek(0)
                self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected note literal after plus{self.log_tk()}")
                self.restore_to(TokenType.SPACE)
                expression = errExpr(err_source)
        # Parse SetTone
        elif self.match(TokenType.PLUS):
            source = self.advance()
            if self.peek(0).type in NOTES:
                note = self.advance()
                expression = SetTone(1,note,source)
            else:
                self.err_list.append(f"""{SyntaxErr(self.peek(0))}Expected note literal after plus \"{self.source.value}\" {self.log_tk}
| Tip: '+' increase the pitch of a note by a semitone for the entire movement""")                
                expression = errExpr(self.peek(0))
        
        elif self.match(TokenType.DASH):
            source = self.advance()
            if self.peek(0).type in NOTES:
                note = self.advance()
                expression = SetTone(-1,note,source)
            else:
                self.err_list.append(f"""{SyntaxErr(self.peek(0))}Expected note literal after dash \"{self.source.value}\" {self.log_tk}
| Tip: '-' lowers the pitch of a note by a semitone for the entire movement""")
                expression =  errExpr(self.peek(0))

        # Parse SetOctave
        elif self.match(TokenType.GREATER_THAN):
            source = self.advance()
            oct = 0
            if self.match(TokenType.NUM):
                oct = int(self.advance().value)

            expression =SetOctave(1,oct,source)

        # Parse SetOctave        
        elif self.match(TokenType.LESS_THAN):
            source = self.advance()
            oct = 0
            if self.match(TokenType.NUM):
                oct = int(self.advance().value)

            expression = SetOctave(-1,oct,source)

        # Parse SetDuration
        elif self.match(TokenType.COLON):
            source = self.advance()
            
            if self.match(TokenType.NUM):
                x = self.advance()
                over = None
                if self.expect(TokenType.SLASH):
                    over = self.expect(TokenType.NUM)
                
                duration = int(x.value) if over is None else Fraction(int(x.value),int(over.value))

                expression = SetDuration(duration,source)
            else:
                self.err_list.append(f"""{SyntaxErr(self.peek(0))}After colon expression expected number{self.log_tk()}
| Tip: ':' fallowed directly by a number is used to set the duration of a single note for the given track""")
                expression = errExpr(self.peek(0))

        # Parse SetMeasure
        elif self.match(TokenType.BANG):
            source = self.advance()

            if self.match(TokenType.NUM):
                x = int(self.advance().value)

                if self.expect(TokenType.SLASH) is None:
                    err_source = self.peek(-1)
                    self.err_list.append(f"{SyntaxErr(self.peek(-1))}Measures are defined as number/number, after number got {self.peek(-1)} instead of \"/\"  ")
                    self.restore_to(TokenType.SPACE)
                    expression = errExpr(err_source)

                if self.match(TokenType.NUM):
                    over = int(self.advance().value)
                else:
                    self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected number after defining measure{self.log_tk()}")
                    self.restore_to(TokenType.SPACE)

                expression = SetMeasure(x,over,source)
            else:
                self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected a number after \"!\"{self.log_tk()} ")
                self.restore_to(TokenType.SPACE)


        # Parse SetTempo
        elif self.match(TokenType.CARROT):
            source = self.advance()

            if self.match(TokenType.NUM):
                x = int(self.advance().value)

                tempo = x
                expression =SetTempo(tempo,source)
            else:
                self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected number after '^'",self.log_tk())
                self.restore_to(TokenType.SPACE)

        # Parse Bar
        elif self.match(TokenType.PIPE):
            expression =Bar(self.advance())

        # Parse SetInterval
        elif self.match(TokenType.NUM):
            # it's a duration
            expression =SetInterval(self.advance())


# compound expressions

        # Parse Repetition
        elif self.match(TokenType.ASTERISK):
            source = self.advance()
            n = int(self.advance().value)
            if self.stack[-1] == ParseState.EXPR:
                expression = Repetition(n,source)
            else:
                self.err_list.append(f"{SyntaxErr(self.peek(0))}Repetition postfix operator can only be used after an expression{self.log_tk()}")

        # Parse ReleaseNote
        elif self.match(TokenType.CLOSE_PAREN):
            source = self.advance()
            if self.stack[-1] == ParseState.EXPR:
                expression = ReleaseNote(source)
            else:
                self.err_list.append(f"{SyntaxErr(self.peek(0))}Close paren postfix operator can only be used after an expression{self.log_tk()}")

        # Parse HoldNote
        elif self.match(TokenType.OPEN_PAREN):
            #parse hold
            source = self.advance()
            note = self.parse_expr()
            if isinstance(note,Note) or isinstance(note,Chord) or isinstance(note,Ident):
                expression =HoldNote(note,source)
            else:
                self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected note or identifier after open parenthesis{self.log_tk()}")
                self.retore_to_space()

        # Parse ExprGroup
        elif self.match(TokenType.OPEN_BRACKET):

            source = self.advance()
            self.skip_whitespace()
            exprs = []
            # gotta parse a expr group
            while not self.match(TokenType.CLOSE_BRACKET):
                exprs.append(self.parse_expr())
                self.skip_whitespace() #whitespace doesn't matter within a expr group
            
            self.advance() # skip close bracket

            # space doesn't matter after parsing an expr
            self.skip_space()
            
            expression =ExprGroup(exprs,source)


        # Parse ident or chord
        elif self.match(TokenType.ALPHANUM):
            ident = self.advance()

            if ident.value not in self.idents.keys():
                self.idents[ident.value] = ident

            if self.match(TokenType.SLASH):
                # parsing chord
                self.advance()
                curr_ident = Ident(ident)
                notes = [curr_note]
                while self.peek(0).type not in [TokenType.NL, TokenType.SPACE]:
                    ident = self.parse_expr()
                    if isinstance(ident,Note):
                        notes.append(ident)
                        self.stack.pop()
                        return Chord(notes,ident)
                    
                    if isinstance(ident,Chord):
                        notes.extend(ident.notes)
                        self.stack.pop()
                        return Chord(notes,ident)

                    if isinstance(ident,Ident):
                        notes.append(ident)
                        self.stack.pop()
                        return Chord(notes,ident)


                    self.err_list.append(f"{SyntaxErr(self.peek(0))}Chords can only be formed from notes,using \"{ident.value}\" is not valid")
                    self.restore_to(TokenType.SPACE)
            
            # parse Macro appl
            elif self.match(TokenType.OPEN_PAREN):
                self.advance()
                self.skip_space()
                args = []
                while True:
                    args.append(self.parse_expr())
                    
                    self.skip_whitespace()

                    if self.expect(TokenType.CLOSE_PAREN):
                        break
                    
                    if self.expect(TokenType.COMMA):
                        continue
                    else:
                        self.err_list.append(f"{SyntaxErr(self.peek(0))}Expected comma or close parenthesis after expression in argument list",self.log_tk())
                        self.restore_to(TokenType.CLOSE_PAREN)

                self.stack.pop() # preserve parse stack state
                return MacroCall(ident,args)
            elif self.match(TokenType.SPACE):
                pass
            elif self.match(TokenType.NL):
                pass
            elif self.match(TokenType.CLOSE_PAREN):
                pass
            else :
                self.err_list.append(f"{SyntaxErr(self.peek(0))}Unexpected token after identifier{self.peek(0).value}")
                expresion = errExpr(self.peek(0))
                self.restore_to(TokenType.SPACE)

            # if it doesn't match anything else, it's just an identifier
            expression =Ident(ident)

        
        # Parse Note or chord
        elif self.peek(0).type in NOTES:
            # parse notes
            note_p = self.advance()

            semitone = 999 # placeholder for default value
            octave = -1 # placeholder for default value
            duration = -1 # placeholder for default value
            # parse semitones 
            while True:
                if self.match(TokenType.PLUS):
                    semitone +=1
                    self.advance()
                elif self.match(TokenType.DASH):
                    semitone -=1
                    self.advance()
                else:
                    break


            if self.match(TokenType.DOT):
                self.advance()
                if self.match(TokenType.NUM):
                    octave = self.advance()

            if self.match(TokenType.SLASH):
                # parsing chord
                self.advance() #consume slash
                curr_note = Note(note_p,semitone,octave,duration)
                notes = [curr_note]
                while self.peek(0).type not in [TokenType.NL, TokenType.SPACE]:
                    note = self.parse_expr()
                    if isinstance(note,Note):
                        notes.append(note)
                        self.stack.pop()
                        return Chord(notes,note_p)
                    
                    elif isinstance(note,Chord):
                        notes.extend(note.notes)
                        self.stack.pop()
                        return Chord(notes,note_p)

                    elif isinstance(note,Ident):
                        notes.append(note)
                        self.stack.pop()
                        return Chord(notes,note_p)

                    else:
                        self.err_list.append(f"{SyntaxErr(self.peek(0))}Chords can only be formed from notes,using {note} is not valid, notes= {notes}, curr{self.peek(0)}")
                        

            if self.match(TokenType.COLON):
                self.advance()

                if self.match(TokenType.NUM):
                    duration = float(self.advance().value)
                elif self.match(TokenType.SLASH):
                    self.advance() #consume slash token

                    if self.match(TokenType.NUM):
                        duration = Fraction(1,int(self.advance().value))
                    else:
                        self.err_list.append(f"{SyntaxErr(self.peek(0))}After slash expected a number",self.log_tk())
                        self.restore_to(TokenType.SPACE)

                else :
                    self.err_list.append(f"{SyntaxErr(self.peek(0))}After colon in note definition expected a number",self.log_tk())
            
            expression =Note(note_p,semitone,octave,duration)
        elif self.match(TokenType.EOF):
            pass

        else:
            self.err_list.append(f"{SyntaxErr(self.peek(0))}Unexpected token while parsing expressions: {self.peek(0).value} ")

        top = self.stack.pop()
        if top != ParseState.EXPR:
            self.dump_state()
            raise ValueError(f"Expected expr on top of the stack, got {top} instead")

        if expression is None:
            self.dump_state()
            raise ValueError(f"Expression must not be none",self.log_tk())

        return expression


# helper parser functions
    def skip_space(self):
        self.log(f"skip space after {self.peek(0)}")
        while self.peek(0).type == TokenType.SPACE:
            self.advance()

    def skip_whitespace(self):
        self.log(f"skip whitespace after {self.peek(0)}")
        while self.peek(0).type == TokenType.SPACE or self.peek(0).type == TokenType.NL:
            self.advance()

    def skip_newlines(self):
        self.log(f"skip newline after {self.peek(0)}")
        """Skip any newline tokens"""
        while self.peek(0).type == TokenType.NL:
            self.advance()

    def log_tk(self):
        return f", got token \"{self.peek(0).value}\" instead\n"

    def dump_state(self):
        print(self.stack)
        print("Recent tokens")
        for tk in self.tokens[self.pos - 5 : self.pos + 5]:
            print(tk)

        print("Recent logs:")
        for log in self.log_list[-10:]:
            print(log)

        print("Errors found:")
        for err in self.err_list:
            print(err)

# error recovery parser functions
    def restore_stmt(self):
       
        self.log(f"restore statement from error at {self.peek(0)}")
        if self.peek(0).type == TokenType.OPEN_BRACKET:
                self.restore_to(TokenType.CLOSE_BRACKET)
        while self.peek(0).type != TokenType.NL and \
                self.peek(0).type != TokenType.COLON and \
                self.peek(0).type != TokenType.EOF :
            self.advance()


    def restore_to(self,*args):
        self.log(f"restore to {args} from error at {self.peek(0)}")
        while self.peek(0).type not in args:
            self.advance()


# helper err functions
def SyntaxErr(token):
    return f"Syntax Error({token.line},{token.column}):"

def Ident_err(token):
    return f"Identifier Error({token.line},{token.column}):"

